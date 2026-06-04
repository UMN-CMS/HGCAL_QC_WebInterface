#!/usr/bin/python3

"""
Export EngineDB QC grading information into the CSV + YAML pair consumed by
``csv_to_xml.py --task qc_grade``.

Script produces two outputs:
  * a CSV with one row per part:
        LABEL_TYPECODE, SERIAL_NUMBER, QUALITY, COMMENT_DESCRIPTION
  * a YAML run-info file:
        RUN_NAME, RUN_BEGIN_TIMESTAMP, RUN_END_TIMESTAMP, USER
        (and an optional COMMENT_DESCRIPTION)

Minimal usage (only --user is required; everything else uses defaults):
    python3 qc_grade_export.py --user "Jeremy Mans"

Full usage (all arguments):
    python3 qc_grade_export.py \\
        --user "Jeremy Mans" \\
        --run-name "UMN_engines_batch3" \\
        --output engine_grades.csv \\
        --runinfo engine_qcrun.yaml \\
        --comment "Bulk historical QC grade upload"
"""

import argparse
import csv
import datetime
import logging
import sys

from connect import connect

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Timezone offset appended to the run timestamps (UMN is US/Central:
# -05:00 during daylight saving, -06:00 in winter).
DEFAULT_TZ_OFFSET = "-05:00"


def typecode_from_type_id(type_id):
    """'EL10E2' -> 'EL-10E2' (matches the LABEL_TYPECODE used by the
    registration scripts)."""
    if not type_id or len(type_id) <= 2:
        return None
    return f"{type_id[:2]}-{type_id[2:]}"


def fetch_latest_grades(cur):
    """Return latest grade per board as a list of dicts, ordered by time."""
    cur.execute(
        """
        SELECT b.full_id, b.type_id, g.grade, g.comments, p.person_name, g.grading_time
        FROM Grades g
        JOIN Board b   ON g.board_id  = b.board_id
        JOIN People p  ON g.person_id = p.person_id
        JOIN (
            SELECT board_id, MAX(grade_id) AS grade_id
            FROM Grades
            WHERE (board_id, grading_time) IN (
                SELECT board_id, MAX(grading_time) FROM Grades GROUP BY board_id
            )
            GROUP BY board_id
        ) latest ON g.grade_id = latest.grade_id
        ORDER BY g.grading_time, g.grade_id
        """
    )
    rows = []
    for full_id, type_id, grade, comments, person, gtime in cur.fetchall():
        typecode = typecode_from_type_id(type_id)
        if typecode is None:
            logger.warning("Skipping %s: cannot derive LABEL_TYPECODE from type_id %r", full_id, type_id)
            continue
        rows.append({
            "LABEL_TYPECODE": typecode,
            "SERIAL_NUMBER": full_id,
            "QUALITY": grade,
            "COMMENT_DESCRIPTION": (comments or "").strip(),
            "_person": person,
            "_time": gtime,
        })
    return rows


def write_csv(rows, out_path):
    fields = ["LABEL_TYPECODE", "SERIAL_NUMBER", "QUALITY", "COMMENT_DESCRIPTION"]
    fh = open(out_path, "w", newline="") if out_path else sys.stdout
    try:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    finally:
        if out_path:
            fh.close()
    logger.info("CSV: wrote %d part(s) to %s", len(rows), out_path or "<stdout>")


def _yaml_quote(value):
    """Double-quote a scalar for YAML, escaping backslashes and quotes."""
    return '"%s"' % str(value).replace("\\", "\\\\").replace('"', '\\"')


def fmt_timestamp(dt, tz_offset):
    """datetime -> 'YYYY-MM-DD HH:mm:ss+TZ:TZ'."""
    return dt.strftime("%Y-%m-%d %H:%M:%S") + tz_offset


def write_yaml(rows, out_path, run_name, user, tz_offset, comment=None):
    if not rows:
        raise RuntimeError("No graded parts found; refusing to write an empty run.")
    begin = min(r["_time"] for r in rows)
    end = max(r["_time"] for r in rows)

    lines = [
        "RUN_NAME: %s" % _yaml_quote(run_name),
        "RUN_BEGIN_TIMESTAMP: %s" % _yaml_quote(fmt_timestamp(begin, tz_offset)),
        "RUN_END_TIMESTAMP: %s" % _yaml_quote(fmt_timestamp(end, tz_offset)),
        "USER: %s" % _yaml_quote(user),
    ]
    if comment:
        lines.append("COMMENT_DESCRIPTION: %s" % _yaml_quote(comment))
    content = "\n".join(lines) + "\n"

    if out_path:
        with open(out_path, "w") as fh:
            fh.write(content)
    else:
        sys.stdout.write(content)
    logger.info("YAML: run '%s' spanning %s .. %s -> %s",
                run_name, fmt_timestamp(begin, tz_offset), fmt_timestamp(end, tz_offset),
                out_path or "<stdout>")


def run(args):
    db = connect(0)
    cur = db.cursor(buffered=True)
    try:
        rows = fetch_latest_grades(cur)
        logger.info("Found %d graded engine(s)", len(rows))
        if not rows:
            logger.error("Nothing to export.")
            return 1

        persons = sorted({r["_person"] for r in rows})
        if len(persons) > 1:
            logger.warning("Grades span multiple testers %s; all attributed to USER=%r in the run.",
                           persons, args.user)

        write_csv(rows, args.output)
        write_yaml(rows, args.runinfo, args.run_name, args.user, DEFAULT_TZ_OFFSET, args.comment)
        return 0
    finally:
        cur.close()
        db.close()


def run_cli():
    parser = argparse.ArgumentParser(
        description="Export EngineDB QC grades to the CSV + YAML consumed by csv_to_xml.py --task qc_grade."
    )
    parser.add_argument("-o", "--output", default="grades.csv",
                        help="Output CSV file (default: grades.csv; '-' for stdout)")
    parser.add_argument("-y", "--runinfo", default="qcrun.yaml",
                        help="Output run-info YAML file (default: qcrun.yaml)")
    parser.add_argument("--run-name", default=None,
                        help="Unique RUN_NAME (default: engine_qc_grade_<today>)")
    parser.add_argument("--user", required=True,
                        help="USER string: who was responsible for the QC data taking")
    parser.add_argument("--comment", default=None,
                        help="Optional COMMENT_DESCRIPTION for the run (YAML-level)")
    args = parser.parse_args()

    if args.output == "-":
        args.output = None
    if args.run_name is None:
        today = datetime.date.today().isoformat()
        args.run_name = f"engine_qc_grade_{today}"

    return run(args)


if __name__ == "__main__":
    sys.exit(run_cli())

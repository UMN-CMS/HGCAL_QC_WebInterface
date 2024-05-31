import sys
import publish_config
from connect import connect
import os
import makeTestingData

db = connect(0)
cur = db.cursor()

local_path = os.path.dirname(os.path.abspath(__file__))

paths = publish_config.get_paths()
for p in paths:
    if not os.path.isdir(p):
        os.makedirs(p)

makeTestingData.run()

db_name = publish_config.get_db_name()
db_lower = db_name.lower()

# gets image names from database
cur.execute('select board_id from Board')
board_id = cur.fetchall()
for b in board_id:
    try:
        cur.execute('select image_name,date from Board_images where board_id=%s and view="Top" order by date desc' % b[0])
        img_name_top = cur.fetchall()[0][0]
        cur.execute('select image_name,date from Board_images where board_id=%s and view="Bottom" order by date desc' % b[0])
        img_name_bottom = cur.fetchall()[0][0]

        # writes images to local files
        with open('/home/ePortage/wagondb/%s' % img_name_top, 'rb') as f:
            img_str = f.read()
        with open('%(path)s/../../static_html/files/%(db)s/%(name)s' % {'path': local_path, 'db': db_lower, 'name': img_name_top}, 'wb') as f:
            f.write(img_str)

        with open('/home/ePortage/wagondb/%s' % img_name_bottom, 'rb') as f:
            img_str = f.read()
        with open('%(path)s/../../static_html/files/%(db)s/%(name)s' % {'path': local_path, 'db': db_lower, 'name': img_name_bottom}, 'wb') as f:
            f.write(img_str)
    except IndexError:
        pass

    
with open('{}/../../static/files/goldy2.png'.format(local_path), 'rb') as tmp:
    img_str = tmp.read()
with open('{}/../../static_html/files/goldy2.png'.format(local_path), 'wb') as f:
    f.write(img_str)

pages = publish_config.get_pages()
for p in pages:
    sys.stdout = open('%(path)s/../../static_html/%(db)s/%(script)s.html' % {'script': p[:-3], 'db': db_name, 'path': local_path}, 'w')
    script = __import__(p[:-3])
    script.run(True) 


looped = publish_config.looped_pages()
for k in looped.keys():
    if k == 'Serial Numbers':
        cur.execute('select full_id, type_id from Board')
        for sn in cur.fetchall():
            for p in looped[k]:
                path = '%(path)s/../../static_html/%(db)s/%(type_id)s_%(sn)s' % {'sn': sn[0], 'type_id': sn[1], 'db': db_name, 'path': local_path}
                sys.stdout = open('%(path)s_%(script)s.html' % {'script': p[:-3], 'path': path}, 'w')
                script = __import__(p[:-3])
                script.run(sn[0], sn[1]) 

    if k == 'Subtypes':
        cur.execute('select type_id from Board')
        for t in cur.fetchall():
            for p in looped[k]:
                path = '%(path)s/../../static_html/%(db)s/%(type_id)s' % {'type_id': t[0], 'db': db_name, 'path': local_path}
                sys.stdout = open('%(path)s_%(script)s.html' % {'script': p[:-3], 'path': path}, 'w')
                script = __import__(p[:-3])
                script.run(t[0]) 

    if k == 'People':
        cur.execute('select person_id,person_name from People')
        for t in cur.fetchall():
            for p in looped[k]:
                path = '%(path)s/../../static_html/%(db)s/%(id)s' % {'id': t[1], 'db': db_name, 'path': local_path}
                sys.stdout = open('%(path)s_%(script)s.html' % {'script': p[:-3], 'path': path}, 'w')
                script = __import__(p[:-3])
                script.run(t[0]) 

    if k == 'Attachments': 
        sys.stdout = sys.__stdout__
        cur.execute('select attach_id from Attachments')
        attach_id = cur.fetchall()
        for a in attach_id:
            for p in looped[k]:
                sys.stdout = open('%(path)s/../../static_html/%(db)s/attach_%(id)s.html' % {'db': db_name, 'id': a[0], 'path': local_path}, 'w')
                script = __import__(p[:-3])
                script.run(a[0])

sys.stdout.close()

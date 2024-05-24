from connect import connect

# this script is no longer used, images are pulled directly from the main machine

db = connect(0)
cur = db.cursor()

# gets image names from database
cur.execute('select board_id from Board where full_id="%s"' % sn)
board_id = cur.fetchall()[0][0]
cur.execute('select image_name,date from Board_images where board_id=%s and view="Top" order by date desc' % board_id)
img_name_top = cur.fetchall()[0][0]
cur.execute('select image_name,date from Board_images where board_id=%s and view="Bottom" order by date desc' % board_id)
img_name_bottom = cur.fetchall()[0][0]

# writes images to local files
with open('/home/ePortage/wagondb/%s' % img_name_top, 'rb') as f:
    img_str = f.read()
with open('../../static/files/temp1', 'wb') as f:
    f.write(img_str)

with open('/home/ePortage/wagondb/%s' % img_name_bottom, 'rb') as f:
    img_str = f.read()
with open('../../static/files/temp2', 'wb') as f:
    f.write(img_str)

import os
import sys
import re
import time
import xmltodict
import sqlite3
from sqlite3 import Error
from urllib.request import urlopen, urlretrieve
from urllib.parse import quote
from mastodon import Mastodon

MASTODON_SERVER = "https://botsin.space"

CHECK_DELAY = 10 * 60  # 10m

RUN_CMD = 'xvfb-run ./application.linux64/D64Draw "{}" "{}" "{}"'

RSS_FEED = "https://csdb.dk/rss/latestadditions.php?type=release"

sql_create_table = """
CREATE TABLE IF NOT EXISTS releases (
    id      TEXT PRIMARY KEY,
    gendate TEXT
);
"""

sql_insert = "INSERT OR REPLACE INTO releases (id, gendate) VALUES (?, CURRENT_DATE);"
sql_select = "SELECT * FROM releases WHERE id=?;"


ex = re.compile('<a href="([^"]+)" title="([^"]+)"\>Download\<\/a\>')


def login_app(user, pw):
    mastodon = Mastodon(client_id="pytooter_clientcred.secret", api_base_url=MASTODON_SERVER)
    mastodon.log_in(user, pw, to_file="pytooter_usercred.secret")
    print("Login for '{}' succesfull".format(user))


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
        sys.exit(1)


def insert_entry(conn, id):
    """
    insert entry for given ID
    """
    cur = conn.cursor()
    cur.execute(sql_insert, (id,))
    conn.commit()
    print("RL: inserted {}".format(id))


def check_entry(conn, id):
    """
    returns TRUE if ID not already generated
    """
    print("RL: checking {}".format(id))
    cur = conn.cursor()
    cur.execute(sql_select, (id,))
    row = cur.fetchone()
    return row is None


def fetch_dict():
    output = urlopen(RSS_FEED).read()
    xml = output.decode("utf-8")
    return xmltodict.parse(xml)


def generate_post(con, mastodon, title, release, download):
    if check_entry(con, release):
        cdir = os.getcwd()

        # download D64
        d64_in = cdir + "/img.d64"
        print("Downloading {}".format(download))
        urlretrieve(download, d64_in)

        # generate image
        png_out = cdir + "/img.png"
        print("Generating {}".format(png_out))
        os.system(RUN_CMD.format(d64_in, png_out, title))

        # post to Mastodon
        print("Posting {}".format(title))
        post_image(mastodon, title, release, png_out)

        # mark as done in DB
        insert_entry(con, release)

    else:
        print("Ignoring duplicate {}".format(title))


def post_image(mastodon, title, url, img):
    rand_media = mastodon.media_post(img, description="D64 disk image visualization: {}".format(title))

    mastodon.status_post(
        "#C64 disk image for #CSDB release:\n{}\n\n{}\n\n#CreativeCoding #BotsOfMastodon #GenerativeArt".format(title, url),
        media_ids=[rand_media["id"]],
        visibility="unlisted",
    )

    os.remove(img)


def do_poll(con, mastodon):
    dic = fetch_dict()

    for e in reversed(dic["rss"]["channel"]["item"]):
        m = ex.search(e["description"])
        if m:
            title = e["title"]
            release_url = e["link"]
            download_url = m[1]
            download_file = m[2]
            if download_file.lower().endswith(".d64"):
                try:
                    generate_post(con, mastodon, title, release_url, download_url)
                except Exception as e:
                    print("generate exception: {}".format(e))
                print("")


def main_app():
    mastodon = Mastodon(access_token="pytooter_usercred.secret", api_base_url=MASTODON_SERVER)
    con = create_connection(r"diskbot.db")
    create_table(con, sql_create_table)
    while True:
        do_poll(con, mastodon)
        print("==================================================")
        time.sleep(CHECK_DELAY)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "register":
        Mastodon.create_app("c64diskbot", api_base_url=MASTODON_SERVER, to_file="pytooter_clientcred.secret")
        print("App registered")
    elif len(sys.argv) == 4 and sys.argv[1] == "login":
        login_app(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "run":
        main_app()
    else:
        print("Usage:")
        print("  {} [register|login|run]".format(sys.argv[0]))

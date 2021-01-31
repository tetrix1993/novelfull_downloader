from apputil import *
import os
import json


BASE_FOLDER = 'download'
BASE_URL = 'https://novelfull.com'
URL_PREFIX = 'https://novelfull.com/index.php/'
NOVELS_JSON_OUTPUT = 'novels.json'
CHAPTERS_JSON = 'chapters.json'
novels = []


def init():
    global novels
    novels = get_novel_json()


def run():
    print('Novelfull Downloader')
    while True:
        print('[INFO] Main Menu')
        print_main_menu_message()
        try:
            choice = int(input('Enter choice: ').strip())
            if choice == 1:
                download_novel()
            elif choice == 2:
                list_novel()
            elif choice == 0:
                break
            else:
                raise Exception
        except:
            print('[ERROR] Invalid choice.')


def print_main_menu_message():
    print('Select choice: ')
    print('1: Download novel by URL')
    print('2: List novel that are downloaded')
    print('0: Exit')


def download_novel():
    global novels
    print('[INFO] Download Novel')
    try:
        url = input('Enter URL: ').strip().split('?')[0]
        if not url.startswith(URL_PREFIX):
            raise Exception
        novel_url = url.split(URL_PREFIX)[1].split('.html')[0]
        novel_id, folder = get_novel_id(novel_url)
        page = 1
        chapters = []
        chapter_id = 0
        while True:
            page_url = url + '?page=' + str(page)
            soup = get_soup(page_url)
            if soup:
                uls = soup.find_all('ul', class_='list-chapter')
                if len(uls) == 0:
                    raise Exception

                if novel_id != len(novels):
                    title = soup.find('h3', class_='title').text
                    novels.append({'id': novel_id, 'title': title, 'url': novel_url})
                    generate_novel_json(novels)
                for ul in uls:
                    lis = ul.find_all('li')
                    for li in lis:
                        a_tag = li.find('a')
                        if a_tag and a_tag.has_attr('title') and a_tag.has_attr('href'):
                            chapter_url = BASE_URL + a_tag['href']
                            title_split = a_tag['title'].split(' ')
                            if len(title_split) > 2:
                                name = replace_bad_characters(title_split[0] + '_' + title_split[1], '')
                            else:
                                continue
                            filepath = folder + '/' + name + '.txt'
                            download_chapter(chapter_url, filepath, a_tag['title'])
                            chapter_id += 1
                            chapters.append({'id': chapter_id, 'name': name, 'title': a_tag['title']})
            else:
                raise Exception
            if not has_next_page(soup, page):
                break
            page += 1
        generate_chapter_json(novel_id, chapters)
    except:
        print('[ERROR] Invalid URL')


def download_chapter(url, output, title):
    if os.path.exists(output):
        print('File exists: %s (%s)' % (output, title))
        return
    try:
        soup = get_soup(url)
        paras = soup.find('div', id='chapter-content').find_all('p')
        ignore_empty_para = True
        with open(output, 'w+', encoding='utf-8') as f:
            for para in paras:
                if len(para.text) == 0 and ignore_empty_para:
                    continue
                else:
                    ignore_empty_para = False
                f.write(para.text + '\n\n')
        print('Downloaded %s' % title)
    except Exception as e:
        print('[ERROR] Error in processing %s' % url)
        print(e)


def list_novel():
    global novels
    print('[INFO] List of Novel')
    printed = 0
    for novel in novels:
        try:
            print('%s: %s' % (str(novel['id']), novel['title']))
            printed += 1
        except:
            continue
    if printed != len(novels):
        print('Not all titles are listed due to error in %s' % NOVELS_JSON_OUTPUT)
    if len(novels) == 0:
        print('[INFO] No novels are downloaded')
    else:
        print('[INFO] End of List of Novel')


def get_novel_json():
    data = []
    if os.path.exists(NOVELS_JSON_OUTPUT):
        try:
            with open(NOVELS_JSON_OUTPUT, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
        except Exception as e:
            print('Error in reading %s' % NOVELS_JSON_OUTPUT)
            print(e)
    return data


def generate_novel_json(novel_list):
    with open(NOVELS_JSON_OUTPUT, 'w+', encoding='utf-8') as f:
        json.dump(novel_list, f)


def generate_chapter_json(novel_id, chapters):
    if len(chapters) > 0:
        folder = BASE_FOLDER + '/' + str(novel_id)
        if not os.path.exists(folder):
            os.makedirs(folder)
        output = folder + '/' + CHAPTERS_JSON
        with open(output, 'w+', encoding='utf-8') as f:
            json.dump(chapters, f)


def get_novel_id(novel_url):
    global novels
    novel_id = -1
    for novel in novels:
        if novel['url'] == novel_url:
            novel_id = novel['id']
    if novel_id == -1:
        novel_id = len(novels) + 1

    save_folder = BASE_FOLDER + '/' + str(novel_id)
    if not os.path.exists(BASE_FOLDER + '/' + str(novel_id)):
        os.makedirs(save_folder)
    return novel_id, save_folder


def has_next_page(soup, page):
    pagination = soup.find('ul', class_='pagination')
    if pagination:
        lis = pagination.find_all('li')
        if len(lis) > 0:
            a_tag = lis[-1].find('a')
            if a_tag and a_tag.has_attr('data-page'):
                try:
                    return page - 1 < int(a_tag['data-page'])
                except:
                    pass
    return False


def close():
    pass


if __name__ == '__main__':
    init()
    run()
    close()

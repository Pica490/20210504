import requests
from pprint import pprint
from datetime import datetime
import json
import os

class VkUnloader:
    def __init__(self, user_id):
        self.user_id = user_id

    def rename_list(self, list_photos, res):
        n = list_photos[len(list_photos)-1]['photo_name']
        i = 0
        for name in list_photos:
            if name['photo_name'] == n:
                s = int(res['response']['items'][i]['date'])
                s_datetime = datetime.utcfromtimestamp(s).strftime('%Y%m%d')
                list_photos[i]['photo_name'] = str(name['photo_name'][:-4]) + '_' + str(s_datetime) + '.jpg'
                i = i + 1
            n = name['photo_name']
        return list_photos

    def chose_max_size(self, values):
        maximum = 0
        for sizes in values['sizes']:
            if sizes['height'] > maximum:
                max_url = sizes['url']
                max_type = sizes['type']
        return max_url, max_type

    def _get_photos(self, user_id):
        URL = 'https://api.vk.com/method/photos.get'
        params = {
        'user_id': user_id,
        'access_token': ' ', # токен и версия api являются обязательными параметрами во всех запросах к vk\n",
        'v':'5.130',
        'album_id' : 'profile',
        'extended' : '-1'
        }
        res = (requests.get(URL, params=params)).json()
        list_photos = []

        for values in res['response']['items']:
            list_v = self.chose_max_size(values)
            list_photos.append({'photo_url': list_v[0], 'photo_name': str(values['likes']['count']) + '.jpg', 'size': list_v[1]})

        self.rename_list(list_photos,res)

        pprint(list_photos)
        return list_photos

    def write_result(self, photo):
        data = {'file_name' : photo['photo_name'], 'size' : photo['size']}
        a = []
        if not os.path.isfile('result.json'):
            a.append(data)
            with open('result.json', mode='w') as f:
                f.write(json.dumps(a, indent=2))
        else:
            with open('result.json') as feedsjson:
                feeds = json.load(feedsjson)

            feeds.append(data)
            with open('result.json', mode='w') as f:
                f.write(json.dumps(feeds, indent=2))
        return print(f'Данные {data} добавлены в файл result.')

    def upload_file_to_disk(self, list_photos, token):

        url_f = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {'Authorization': token}
        params_1 = {'path': 'Photos/'}
        requests.put(url_f, headers = headers, params = params_1)

        for photo in list_photos:
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            headers = {'Authorization': token}
            params = {'url': photo['photo_url'], 'path' : 'Photos/' + photo['photo_name']}
            response = requests.post(upload_url, headers = headers, params = params)
            response.raise_for_status()

            if response.status_code == 202:
                print("Success")
            self.write_result(photo)

if __name__ == '__main__':
    vk_unload = VkUnloader('2190409')
    token = ' '
    result = vk_unload._get_photos('2190409')
    result2 = vk_unload.upload_file_to_disk(result, token)
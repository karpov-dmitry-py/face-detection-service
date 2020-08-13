import requests
import os.path

# FACECLOUD_API_LOGIN = 'dem0schase@gmail.com'
# FACECLOUD_API_PSWD = 'facecloudpswd'

ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJmNDNkNWVlMi0wMDc1LTRlMjktOWI3NC0xZDY2ZjVhYjk3MDciLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoxMTUsImlhdCI6MTU5NzE4MDY5NCwibmJmIjoxNTk3MTgwNjk0LCJmcmVzaCI6ZmFsc2V9.9NLmhYNgiaiNpSAUVPCENzJDoLpvc4NBearY_iA-kd8'
DETECT_URL = 'https://backend.facecloud.tevian.ru/api/v1/detect'
IMAGES_DIR = 'static/user_images'
HEADERS = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'image/jpeg',
    'Accept': 'application/json',
}


class FaceDetector():

    def __init__(self, filename, images_dir=None):
        self.filename = filename
        images_dir = images_dir if images_dir else IMAGES_DIR
        self.images_dir_full_path = os.path.normpath(os.path.join(os.path.dirname(__file__), images_dir))

    def get_detections(self):
        result = {
            'message': '',
            'data': [],
        }

        filepath = os.path.join(self.images_dir_full_path, self.filename)
        if not (os.path.exists(filepath) and os.path.isfile(filepath)):
            result['message'] = f'File {self.filepath} not found\n'
            return result

        with open(filepath, 'rb') as file:
            response = requests.post(DETECT_URL, data=file, headers=HEADERS)
            json = response.json()
            status_code = json.get('status_code')
            data = json.get('data')
            if not (status_code == 200 and data):
                result['message'] = response.text
                return result

            result['message'] = 'success'
            rows = []
            for item in data:
                coords = item.get('bbox')
                row = {}
                row['x'] = coords['x']
                row['y'] = coords['y']
                row['width'] = coords['width']
                row['height'] = coords['height']
                rows.append(row)

            result['data'] = rows
            return result


def main():
    detector = FaceDetector('some_image_to_process.jpg')
    result = detector.get_detections()


if __name__ == '__main__':
    main()

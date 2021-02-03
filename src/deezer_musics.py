from pydeezer import Deezer, Downloader
from pydeezer.constants import track_formats
from os import path, mkdir, listdir

download_dir = "/home/pi/Music/"


def directory_create(directory):
    if not path.exists(directory):
        try:
            print("creating a new directory for the playlist")
            mkdir(directory)
        except OSError:
            print("Creation of the directory %s failed" % directory)
            return False
    return True


class Deezer_Musics():
    def __init__(self):
        self.deezer = Deezer()
        self.credentials = open('/home/pi/Music/deezer_id.txt').readlines()
        self.arl = self.credentials[0].replace("\n", '')
        self.playlist1_id = self.credentials[1]
        self.user_info = self.deezer.login_via_arl(self.arl)
        self.playlist1 = self.deezer.get_playlist(self.playlist1_id)

    def get_playlist_songs(self):
        '''Return a list of track id'''
        # Available keys : ['DATA', 'COMMENTS', 'CURATOR', 'SONGS']
        songs = self.playlist1['SONGS']['data']

        # song keys are : ['SNG_ID', 'PRODUCT_TRACK_ID', 'UPLOAD_ID', 'SNG_TITLE', 'ART_ID', 'PROVIDER_ID', 'ART_NAME', 'ARTIST_IS_DUMMY', 'ARTISTS', 'ALB_ID', 'ALB_TITLE', 'TYPE', 'MD5_ORIGIN', 'VIDEO', 'DURATION', 'ALB_PICTURE', 'ART_PICTURE', 'RANK_SNG', 'FILESIZE_AAC_64', 'FILESIZE_MP3_64', 'FILESIZE_MP3_128', 'FILESIZE_MP3_256', 'FILESIZE_MP3_320', 'FILESIZE_MP4_RA1', 'FILESIZE_MP4_RA2', 'FILESIZE_MP4_RA3', 'FILESIZE_FLAC', 'FILESIZE', 'GAIN', 'MEDIA_VERSION', 'DISK_NUMBER', 'TRACK_NUMBER', 'TRACK_TOKEN', 'TRACK_TOKEN_EXPIRE', 'VERSION', 'MEDIA', 'EXPLICIT_LYRICS', 'RIGHTS', 'ISRC', 'DATE_ADD', 'HIERARCHICAL_TITLE', 'SNG_CONTRIBUTORS', 'LYRICS_ID', 'EXPLICIT_TRACK_CONTENT', '__TYPE__']
        songs_id = []
        for song in songs:
            songs_id.append(song['SNG_ID'])
        return(songs_id)


if __name__ == "__main__":
    print('Getting datas...')
    music = Deezer_Musics()
    songs_id = music.get_playlist_songs()
    playlist_path = download_dir+music.playlist1['DATA']['TITLE']+'/'
    if directory_create(playlist_path):
        songs_already_downloaded = [file for file in listdir(playlist_path) if '.mp3' in file]
        print(songs_already_downloaded)
        # for song in songs_already_downloaded:
        #     if '.mp3' not in song:
        #         continue
        #     if song

        print('Downloading datas...')

        downloader = Downloader(music.deezer, songs_id, download_dir,
                                quality=track_formats.MP3_320, concurrent_downloads=4)
        downloader.start()

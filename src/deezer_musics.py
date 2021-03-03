from pydeezer import Deezer, Downloader
from pydeezer.constants import track_formats
from os import path, mkdir, listdir, remove
from mutagen import File as mutagen_File

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


def compare_already_downloaded_songs(playlist_path, songs, return_rm=False):
    ''' Return songs id list to download from a playlist path and a songs list
        If return_rm then return a list of songs filenames to remove '''

    song_files = [file for file in listdir(playlist_path) if '.mp3' in file]
    songs_existing = []
    for song_file in song_files:
        tags = mutagen_File(playlist_path + song_file)
        # del tags["APIC:"]
        # dict_keys(['TIT2', 'TPE1', 'TRCK', 'TALB', 'TPOS', 'TDRC', 'TCON', 'TSRC', 'TPE2', 'TPUB', 'TCOP', 'APIC:'])
        title = str(tags["TIT2"])  # Get the name of the track
        start = title.find('(')
        end = title.find(')')
        if start != -1 and end != -1:
            title = title[:start-1]+title[end+1:]
        authors = str(tags["TPE2"])  # Get author of the published music
        songs_existing.append((title, authors))

    songs_to_download = []
    for song in songs:
        title = song['SNG_TITLE']
        start = title.find('(')
        end = title.find(')')
        if start != -1 and end != -1:
            title = title[:start-1]+title[end+1:]
        authors = song['ART_NAME']
        songs_to_download.append((title, authors))

    difference = list(set(songs_to_download) - set(songs_existing))
    real_songs_to_download = []
    for song in difference:
        real_songs_to_download.append(songs[songs_to_download.index(song)]['SNG_ID'])
    if return_rm:
        difference_rm = list(set(songs_existing) - set(songs_to_download))
        files_rm = [song_files[songs_existing.index(title_art)] for title_art in difference_rm]
        return(real_songs_to_download, files_rm)
    else:
        return(real_songs_to_download)


class Deezer_Musics():
    def __init__(self):
        self.deezer = Deezer()
        self.credentials = open('/home/pi/Music/deezer_id.txt').readlines()
        self.arl = self.credentials[0].replace("\n", '')
        self.playlists_id = self.credentials[1:]
        self.user_info = self.deezer.login_via_arl(self.arl)
        self.playlists = [self.deezer.get_playlist(pid) for pid in self.playlists_id]

    def get_playlists_songs(self):
        '''Return a list of list of track id'''
        # Available keys : ['DATA', 'COMMENTS', 'CURATOR', 'SONGS']
        playlists_songs = [playlist['SONGS']['data'] for playlist in self.playlists]

        # song keys are : ['SNG_ID', 'PRODUCT_TRACK_ID', 'UPLOAD_ID', 'SNG_TITLE', 'ART_ID', 'PROVIDER_ID', 'ART_NAME', 'ARTIST_IS_DUMMY', 'ARTISTS', 'ALB_ID', 'ALB_TITLE', 'TYPE', 'MD5_ORIGIN', 'VIDEO', 'DURATION', 'ALB_PICTURE', 'ART_PICTURE', 'RANK_SNG', 'FILESIZE_AAC_64', 'FILESIZE_MP3_64', 'FILESIZE_MP3_128', 'FILESIZE_MP3_256', 'FILESIZE_MP3_320', 'FILESIZE_MP4_RA1', 'FILESIZE_MP4_RA2', 'FILESIZE_MP4_RA3', 'FILESIZE_FLAC', 'FILESIZE', 'GAIN', 'MEDIA_VERSION', 'DISK_NUMBER', 'TRACK_NUMBER', 'TRACK_TOKEN', 'TRACK_TOKEN_EXPIRE', 'VERSION', 'MEDIA', 'EXPLICIT_LYRICS', 'RIGHTS', 'ISRC', 'DATE_ADD', 'HIERARCHICAL_TITLE', 'SNG_CONTRIBUTORS', 'LYRICS_ID', 'EXPLICIT_TRACK_CONTENT', '__TYPE__']
        playlists_songs_id = []
        for songs in playlists_songs:
            songs_id = []
            for song in songs:
                songs_id.append(song['SNG_ID'])
            playlists_songs_id.append(songs_id)
        return(playlists_songs, playlists_songs_id)


if __name__ == "__main__":
    print('Getting datas...')
    music = Deezer_Musics()
    playlists_songs, playlists_songs_id = music.get_playlists_songs()
    for i, (songs, songs_id) in enumerate(zip(playlists_songs, playlists_songs_id)):
        print("\nChecking playlist", music.playlists[i]['DATA']['TITLE'])
        playlist_path = download_dir+music.playlists[i]['DATA']['TITLE']+'/'
        if directory_create(playlist_path):
            songs_id, songs_rm = compare_already_downloaded_songs(playlist_path, songs, True)
            if songs_rm != []:
                for song_file in songs_rm:
                    remove(playlist_path+song_file)
                    lyric_file = ''.join(song_file.split(".")[:-1])+'.lrc'
                    if lyric_file in listdir(playlist_path):
                        remove(playlist_path+lyric_file)
                        print(f"Removed {playlist_path+song_file} plus its lyrics")
                    else:
                        print(f"Removed {playlist_path+song_file}")
            if songs_id == []:
                print('Nothing to download in this playlist')
            else:
                print('Downloading datas...')

                downloader = Downloader(music.deezer, songs_id, playlist_path,
                                        quality=track_formats.MP3_320, concurrent_downloads=4)
                downloader.start()

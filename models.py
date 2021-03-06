import datetime
import uuid
import re
import string
import os
import copy
from multiprocessing import Process
from datetime import date, datetime
import time
from uuid import uuid3

class Playlist:
    pass

class Album:
    pass



class ClassMethods:
    def __init__(self):
        self.id = None
        self.FILE_PATH = f"dir_data/{self.__class__.__name__.lower()}.txt"

    def save(self):
        class_dict = copy.deepcopy(self.__dict__)
        del class_dict["FILE_PATH"]
        if hasattr(self, "created_by"):
            class_dict["created_by"] = self.created_by.__dict__
        if hasattr(self, "album"):
            class_dict["album"] = self.album.__dict__
        if hasattr(self, "playlist"):
            class_dict["playlist"] = self.playlist.__dict__
        if hasattr(self, "song"):
            class_dict["song"] = self.song.__dict__
        if os.path.isfile(self.FILE_PATH):
            with open(self.FILE_PATH, "r") as file:
                lines = file.readlines()
                for line in lines:
                    if str(self.id) in line:
                        raise Exception(f"ERROR: {type(self)} object is already saved")
        with open(self.FILE_PATH, "a") as file:
            file.write("".join([str(class_dict), str("\n")]))

    def delete(self):
        flag = True
        with open(self.FILE_PATH, "r") as file:
            lines = file.readlines()
        with open(self.FILE_PATH, "w") as file:
            for line in lines:
                if not str(self.id) in line:
                    file.write(line)
                else:
                    flag = False
            if flag is True:
                raise Exception(f"ERROR: {type(self)} object is not saved")

    def update(self, **kwargs):
        class_dict = copy.deepcopy(self.__dict__)
        del class_dict["FILE_PATH"]
        for key, value in kwargs.items():
            if class_dict.get(key):
                class_dict[key] = value
        with open(self.FILE_PATH, "r") as file:
            lines = file.readlines()
        with open(self.FILE_PATH, "w") as file:
            for line in lines:
                if self.id in line:
                    file.write(str(class_dict))
                else:
                    file.write(line)

    @staticmethod
    def filter_1(file_path, **kwargs):
        keywords = ["'{}': '{}'".format(key, value) for key, value in kwargs.items()]
        rows = []
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                count = 0
                for keyword in keywords:
                    if keyword in line:
                        count += 1
                if count == len(keywords):
                    rows.append(line)
        if not rows:
            raise Exception("ERROR: object is not found")
        return rows

    @staticmethod
    def get_1(file_path, **kwargs):
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                for key, value in kwargs.items():
                    if value in line:
                        return line


class UserError(Exception):
    pass


class User(ClassMethods):

    USER_FILE_PATH = os.path.normpath("./dir_data/user.txt")

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        profile_pic: str = None,
        birth_data: datetime = None,
        level: int = 0,
    ):
        super().__init__()
        self.id = str(uuid3(uuid.NAMESPACE_URL, f"{email}_{first_name}_{last_name}"))
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.profile_pic = profile_pic
        self.birth_data = birth_data
        self.level = level

        self.validate()

    def __repr__(self):
        return f"First-name: {self.first_name}, Last-name: {self.last_name}, Email: {self.email} "

    def __validate_none_values(self):
        if (
            self.first_name is None
            or self.last_name is None
            or self.email is None
            or self.password is None
        ):
            raise UserError(
                "Found None in required (first_name,last_name,email,password) fields"
            )

    def __validate_missing_fields(self):
        if not (
            self.first_name.strip()
            and self.last_name.strip()
            and self.email.strip()
            and self.password.strip()
        ):
            raise UserError("ERROR: Missing required fields")

    def __validate_password(self):
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[a-z]+\.[a-z]*$", self.email):
            raise UserError("ERROR: Email is not accurate")

        if (
            len(self.password) < 8
            or re.search("[0-9]", self.password) is None
            or re.search("[A-Z]", self.password) is None
            or re.search("[a-z]", self.password) is None
            or re.search("[{}]".format("".join(string.punctuation)), self.password)
            is None
        ):
            raise UserError("ERROR: Invalid password")

    def __validate_birthday(self):
        if self.birth_data is not None:
            try:
                datetime.datetime.strptime(self.birth_data, "%d,%m,%Y")
            except Exception:
                raise UserError("Error: Birthday has invalid format")

    def __validate_last_first_name(self):
        if not self.first_name.isalpha():
            raise UserError("Error: First name should contain only letters")

        if not self.last_name.isalpha():
            raise UserError("Error: Last name should contain only letters")

    def __validate_level(self):
        if not isinstance(self.level, int):
            raise UserError(
                "Error: Expected type int for level found {}".format(type(self.level))
            )

    def validate(self):
        self.__validate_none_values()
        self.__validate_missing_fields()
        self.__validate_password()
        self.__validate_birthday()
        self.__validate_last_first_name()
        self.__validate_level()

    def create_playlist(self, name):
        playlist = Playlist(name, self)
        playlist.save()

    def delete_playlist(self, name: str):
        with open(Playlist.PLAYLIST_FILE_PATH, "r") as file:
            lines = file.readlines()
        with open(Playlist.PLAYLIST_FILE_PATH, "w") as file:
            for line in lines:
                if str(self.__dict__) in line and name in line:
                    pass
                else:
                    file.write(line)

    @staticmethod
    def __validate_get(**kwargs):
        if "email" not in kwargs.keys():
            raise UserError("ERROR: Please, give unique keywords for search: email")

    @staticmethod
    def filter(**kwargs):
        return User.filter_1(User.USER_FILE_PATH, **kwargs)

    @staticmethod
    def get(**kwargs):
        User.__validate_get(**kwargs)
        return User.get_1(User.USER_FILE_PATH, **kwargs)


class Artist(User, ClassMethods):
    ARTIST_FILE_PATH = os.path.normpath("data_dir/artist.txt")

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        about: str,
        profile_pic: str = None,
        birthdate_date: datetime = None,
        level: int = 0,
    ):
        ClassMethods.__init__(self)
        User.__init__(
            self,
            first_name,
            last_name,
            email,
            password,
            profile_pic,
            birthdate_date,
            level,
        )
        self.about = about
        self.listeners_count = 0

    def __repr__(self):
        return f"First-name: {self.first_name}, Last-name: {self.last_name}, Email: {self.email}, About: {self.about}"

    def add_song(
        self,
        title: str,
        artist_name: str,
        duration: int,
        genre: str,
        year: int,
        album: Album,
    ):
        new_song = Song(title, artist_name, duration, genre, year, self, album)
        new_song.save()

    def delete_song(self, song_id):
        with open(Song.SONG_FILE_PATH, "r") as file:
            lines = file.readlines()
        with open(Song.SONG_FILE_PATH, "w") as file:
            for line in lines:
                if str(song_id) in line:
                    pass
                else:
                    file.write(line)

    def create_album(self, title, label, year, list_of_song_url):
        new_album = Album(title, self, label, year)
        path_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.id}_{new_album.id}"))
        file_path = f"dir_data/{path_name}.txt"

        with open(file_path, "a") as fd:
            for song_obj in list_of_song_url:
                fd.write(str(song_obj.__dict__))

        return new_album

    def delete_album(self, album_id: Album):
        path_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.id}_{album_id.id}"))
        file_path_album_songs = f"dir_data/{path_name}.txt"
        file_path_album = Album.ALBUM_FILE_PATH
        os.remove(file_path_album_songs)
        flag = True
        with open(file_path_album, "r") as file:
            lines = file.readlines()
        with open(file_path_album, "w") as file:
            for line in lines:
                if not str(album_id.id) in line:
                    file.write(line)
                else:
                    flag = False
            if flag is True:
                raise Exception("ERROR:Song object is not saved")

    @staticmethod
    def __validate_get(**kwargs):
        if "email" not in kwargs.keys():
            raise Exception("ERROR: Please, give unique keywords for search: email")

    @staticmethod
    def filter(**kwargs):
        return Artist.filter_1(Artist.ARTIST_FILE_PATH, **kwargs)

    @staticmethod
    def get(**kwargs):
        Artist.__validate_get(**kwargs)
        return Artist.get_1(Artist.ARTIST_FILE_PATH, **kwargs)


class SongError(Exception):
    pass


class Song(ClassMethods):
    SONG_FILE_PATH = os.path.normpath("dir_data/song_data.txt")

    def __init__(
        self,
        title: str,
        artist_name: str,
        duration: int,
        genre: str,
        year: int,
        created_by: Artist,
        album: Album,
    ):
        super().__init__()
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{title}_{artist_name}"))
        self.title = title
        self.artist_name = artist_name
        self.duration = duration
        self.genre = genre
        self.year = year
        self.created_by = created_by
        self.album = album
        self.streams_count = 0
        self.validate()

    def __repr__(self):
        return f"{self.title}- {self.artist_name}"

    def __validate_created_by(self):
        if not isinstance(self.created_by, Artist):
            raise UserError("ERROR: Access denied")

    def __validate_year(self):
        this_year = date.today()
        the_year = this_year.year
        if self.year > the_year:
            raise SongError("ERROR: Song release year should not exceed current year")

    def validate(self):
        self.__validate_year()
        self.__validate_created_by()

    @staticmethod
    def __validate_get(**kwargs):
        if "title" not in kwargs.keys() or "artist_name" not in kwargs.keys():
            raise Exception(
                "ERROR: Please, give unique keywords for search: title and artist_name"
            )

    @staticmethod
    def filter(**kwargs):
        return Song.filter_1(Song.SONG_FILE_PATH, **kwargs)

    @staticmethod
    def get(**kwargs):
        Song.__validate_get(**kwargs)
        return Song.get_1(Song.SONG_FILE_PATH, **kwargs)

    # noinspection PyUnresolvedReferences
    def add_to_playlist(self, playlist: Playlist, user: User):

        # global count
        path_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{playlist.id}_{user.id}"))
        file_path = f"dir_data/{path_name}.txt"

        class_dict = self.__dict__

        if hasattr(self, "created_by"):
            if type(self.created_by) is not dict:
                class_dict["created_by"] = self.created_by.__dict__

        if hasattr(self, "album"):
            if type(self.album) is not dict:
                class_dict["album"] = self.album.__dict__
                if type(self.album["created_by"]) is not dict:
                    self.album["created_by"] = self.album["created_by"].__dict__

        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    if str(self.id) in line:
                        raise Exception("ERROR: Object is already saved Song")
        with open(file_path, "a") as file:
            file.write("".join([str(class_dict), str("\n")]))

    def remove_from_playlist(self, playlist: Playlist, user: User):
        path_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{playlist.id}_{user.id}"))
        file_path = f"dir_data/{path_name}.txt"

        flag = True
        with open(file_path, "r") as file:
            lines = file.readlines()
        with open(file_path, "w") as file:
            for line in lines:
                if not str(self.id) in line:
                    file.write(line)
                else:
                    flag = False
            if flag is True:
                raise Exception("ERROR:Song object is not saved")

    def download(self):
        with open(Song.SONG_FILE_PATH, "r") as df:
            line = df.readline()
            while line:
                if self.id in line:
                    return f"Request song is the following path '{Song.SONG_FILE_PATH}' at position: {df.tell()}"

    def _process_play(self):

        time.sleep(self.duration)
        time_now = time.time()
        if time_now - self.__start > 30:
            self.streams_count += 1

        self.stop(from_process=True)

    def play(self, user: User):

        song_plays = SongPlays(user, self)
        self.__start = song_plays.start_timestamp
        self.process = Process(target=self._process_play)
        self.process.start()

    def stop(self, from_process=False):
        if not from_process:
            self.process.terminate()
        time_now = time.time()
        if time_now - self.__start > 30:
            self.streams_count += 1


class PlaylistError(Exception):
    pass


class Playlist(ClassMethods):
    PLAYLIST_FILE_PATH = os.path.normpath("./dir_data/playlist.txt")

    def __init__(self, name: str, created_by: User, picture_url: str = None):

        super().__init__()
        self.id = str(uuid3(uuid.NAMESPACE_URL, f"{name}_{created_by.id}"))
        self.name = name
        self.data_added = time.time()
        self.created_by = created_by
        self.picture_url = picture_url

        self.genre = set()
        self.count = 0
        self.duration = 0

    def __repr__(self):
        return f"{self.name}, {self.data_added}"

    def count_of_songs(self):

        user_id = self.created_by.id

        path_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.id}_{user_id}"))
        file_path = f"dir_data/{path_name}.txt"
        with open(file_path, "r") as fd:
            lines = fd.readlines()

        return len(lines)

    def duration_of_playlist(self):
        user_id = self.created_by.id
        duration_count = 0
        path_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.id}_{user_id}"))
        file_path = f"dir_data/{path_name}.txt"
        with open(file_path, "r") as fd:
            lines = fd.readlines()
            for line in lines:
                duration_count += dict(**eval(line))["duration"]

        return duration_count

    def genre_list(self):
        user_id = self.created_by.id
        set_genre_list = set()
        path_name = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.id}_{user_id}"))
        file_path = f"dir_data/{path_name}.txt"
        with open(file_path, "r") as fd:
            lines = fd.readlines()
            for line in lines:
                set_genre_list.add(dict(**eval(line))["genre"])
        return set_genre_list

    @staticmethod
    def __validate_get(**kwargs):
        if "created_by" not in kwargs.keys() or "name" not in kwargs.keys():
            raise Exception(
                "ERROR: Please, give unique keywords for search: user and name of the playlist"
            )

    @staticmethod
    def filter(**kwargs):
        return Playlist.filter_1(Playlist.PLAYLIST_FILE_PATH, **kwargs)

    @staticmethod
    def get(**kwargs):
        Playlist.__validate_get(**kwargs)
        return Playlist.get_1(Playlist.PLAYLIST_FILE_PATH, **kwargs)

    def _process_play(self):
        time.sleep(self.__song_duration)
        self.stop(from_process=True)

    def play(self):
        path_name = str(
            uuid.uuid3(uuid.NAMESPACE_DNS, f"{self.id}_{self.created_by.id}")
        )
        file_path = f"dir_data/{path_name}.txt"

        with open(file_path, "r") as fd:
            lines = fd.readlines()
        self.__song_duration = 0
        for line in lines:
            self.__song_duration += dict(**eval(line))["duration"]

        self.process = Process(target=self._process_play)
        self.__start = time.time()
        self.process.start()

    def stop(self, from_process=False):
        if not from_process:
            self.process.terminate()


class Album(Playlist, ClassMethods):
    ALBUM_FILE_PATH = os.path.normpath("dir_data/album.txt")

    def __init__(
        self,
        name: str,
        created_by: Artist,
        label: str,
        year: int,
        picture_url: str = None,
    ):
        ClassMethods.__init__(self)
        Playlist.__init__(self, name, created_by, picture_url)

        self.label = label
        self.year = year
        self.validate()

    def __validate_year(self):
        this_year = date.today()
        the_year = this_year.year
        if self.year > int(the_year):
            raise Exception("ERROR: Album release year should not exceed current year")

    def __validate_user(self):
        if not isinstance(self.created_by, Artist):
            raise Exception("ERROR: Access denied")

    def validate(self):
        self.__validate_year()
        self.__validate_user()

    @staticmethod
    def __validate_get(**kwargs):
        if "created_by" not in kwargs.keys() or "name" not in kwargs.keys():
            raise Exception(
                "ERROR: Please, give unique keywords for search: user and name of the playlist"
            )


class SongPlays(ClassMethods):
    SONG_PLAYS_FILE_PATH = os.path.normpath("data_dir/song_plays.txt")

    def __init__(self, user: User, song: Song):
        super().__init__()
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{user.id}_{song.id}"))
        self.user = user
        self.song = song
        self.start_timestamp = time.time()


class PlaylistSong(ClassMethods):
    PLAYLIST_SONG_FILE_PATH = os.path.normpath("data_dir/playlist_song.txt")

    def __init__(self, playlist: Playlist, song: Song):
        super().__init__()
        self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"{playlist.id}_{song.id}"))
        self.playlist = playlist
        self.song = song
        self.date_added = time.time()


if __name__ == "__main__":
    user = User("Artoik", "Harutyunyan", "asdcds@g.m", "Aa1*dcsc")
    # user.save()
    print(user.filter(email="asdcds@g.m"))

    user_2 = User("Levon", "Harutyunyan", "a@sxscg.m", "Aa1*dcsdcc")
    # user_2.save()

    artist = Artist("Pac", "sxx", "s@s.r", "78Sofi@156", "sss", "sd")
    # artist.save()

    album = Album("name", artist, "esim", 2020)
    # album.save()

    song = Song("song", "Tata", 6, "pop", 2020, artist, album)
    # song.save()

    song_1 = Song("song_1", "guf", 10, "rap", 2001, artist, album)
    # song_1.save()

    play_list = Playlist("Tuyn", user)
    # play_list.save()

    play_list_2 = Playlist("vatacnox", user_2)
    # play_list_2.save()

    # song_1.add_to_playlist(play_list, user)
    # song.add_to_playlist(play_list, user)
    # song_1.add_to_playlist(play_list_2, user_2)
    # song.add_to_playlist(play_list_2, user_2)
    #
    album_song = artist.create_album("esim", "Lcdcd", 2020, [song_1])
    # album_song.save()

    song.play(user)
    play_list.play()
    time.sleep(3)
    play_list.stop()




import vlc
from PyQt6.QtWidgets import QFrame


class VLCPlayer:
    """Wraps a libvlc MediaListPlayer in loop mode. A manual stop()+play()
    inside a MediaPlayerEndReached callback is a known-unstable pattern on
    macOS (crashes when the restart races libvlc's own end-of-stream
    teardown) - PlaybackMode.loop is the supported way to repeat a single
    item forever."""

    def __init__(self, video_frame: QFrame):
        self.instance = vlc.Instance(["--no-osd", "--quiet"])
        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_playback_mode(vlc.PlaybackMode.loop)

        self.mediaplayer = self.list_player.get_media_player()
        self.mediaplayer.set_nsobject(int(video_frame.winId()))

        self.current_path = None

    def play(self, path: str):
        self.current_path = path
        media_list = self.instance.media_list_new([path])
        self.list_player.set_media_list(media_list)
        self.list_player.play()

    def stop_blank(self):
        self.current_path = None
        self.list_player.stop()

    def is_playing(self) -> bool:
        return bool(self.list_player.is_playing())

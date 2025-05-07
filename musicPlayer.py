import os
import random
import time
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import songs
from notification import NotificationLabel

class MusicPlayer:
    def __init__(self, ui):
        self.ui = ui
        # UI Elements Initialization
        self.add_songs_btn = self.ui.add_songs_btn
        self.play_btn = self.ui.play_btn
        self.song_listWidget = self.ui.song_listWidget
        self.favorites_listWidget = self.ui.favorites_listWidget
        self.pause_btn = self.ui.pause_btn
        self.stop_btn = self.ui.stop_btn
        self.next_btn = self.ui.next_btn
        self.previous_btn = self.ui.previous_btn
        self.volumeSlider = self.ui.volumeSlider
        self.music_slider = self.ui.music_slider
        self.songlist_btn = self.ui.songlist_btn
        self.favorites_btn = self.ui.favorites_btn
        self.add_to_fav_btn = self.ui.add_to_fav_btn
        self.shuffle_songs_btn = self.ui.shuffle_songs_btn
        self.loop_one_btn = self.ui.loop_one_btn
        self.remove_selected_btn = self.ui.remove_selected_btn
        self.clear_all_btn = self.ui.clear_all_btn
        self.stackedWidget_2 = self.ui.stackedWidget_2
        self.label_12 = self.ui.label_12
        self.current_song_name_label = self.ui.current_song_name_label
        self.current_song_path_label = self.ui.current_song_path_label
        self.start_time_label = self.ui.start_time_label
        self.end_time_label = self.ui.end_time_label
        self.volume_label = self.ui.volume_label
        
        # player
        self.player = QMediaPlayer()
        self.stopped = False
        self.looped = False
        self.is_shuffled = False
        
        self.slide_index = 0
        self.current_volume = 20
        self.player.setVolume(self.current_volume)
        
        #init slider timer
        self.timer = QTimer(self.ui)
        self.timer.start(1000)
        self.timer.timeout.connect(self.move_slider)
        
        self.player.mediaStatusChanged.connect(self.song_finished)
        self.add_songs_btn.clicked.connect(self.add_songs)
        self.play_btn.clicked.connect(self.play_song)
        self.song_listWidget.itemDoubleClicked.connect(self.play_song)
        self.favorites_listWidget.itemDoubleClicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.stop_btn.clicked.connect(self.stop_song)
        self.next_btn.clicked.connect(self.next_song)
        self.previous_btn.clicked.connect(self.previous_song)
        self.volumeSlider.valueChanged.connect(self.volume_changed)
        self.music_slider.sliderMoved[int].connect(lambda: self.player.setPosition(self.music_slider.value()))
        self.songlist_btn.clicked.connect(self.switch_to_songlist)
        self.favorites_btn.clicked.connect(self.switch_to_favorites)
        self.add_to_fav_btn.clicked.connect(self.favorites_function)
        self.shuffle_songs_btn.clicked.connect(self.shuffle_song)
        self.loop_one_btn.clicked.connect(self.loop_one_song)
        self.remove_selected_btn.clicked.connect(self.remove_selected_song)
        self.clear_all_btn.clicked.connect(self.remove_all_songs)

    def add_songs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self.ui,
            caption='Add Songs',
            directory='./music',
            filter='Supported Files (*.mp3;*.mpeg;*.m4a)'
        )
        if files:
            added_any = False  
            for file in files:
                if file not in songs.current_song_list:
                    songs.current_song_list.append(file)
                    self.song_listWidget.addItem(
                        QListWidgetItem(
                            QIcon(r'icons/MusicListItem.png'),
                            os.path.basename(file)
                        )
                    )
                    added_any = True
            if added_any:
                self.song_listWidget.setCurrentRow(0)
        
    def play_song(self):
        try:
            if self.stackedWidget_2.currentIndex() == 0:
                list_widget = self.song_listWidget
                song_list = songs.current_song_list
            else:
                list_widget = self.favorites_listWidget
                song_list = songs.favorites_songs_list

            current_selection = list_widget.currentRow()
            if current_selection < 0:
                QMessageBox.information(self.ui, 'Play Song', 'Please select a song to play.')
                return

            current_song = song_list[current_selection]
            self.current_song_name_label.setText(os.path.basename(current_song))
            self.current_song_path_label.setText(os.path.dirname(current_song))

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

        except Exception as e:
            print(f'play song error: {e}')

    
    def toggle_pause(self):
        try:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()
            elif self.player.state() == QMediaPlayer.PausedState:
                self.player.play()
        except Exception as e:
            print(f'toggle pause Error: {e}')
    
    def volume_changed(self):
        try:
            self.current_volume = self.volumeSlider.value()
            self.player.setVolume(self.current_volume)
            self.volume_label.setText(f'{self.current_volume}')
        except Exception as e:
            print(f'Changing volume Error: {e}')   
    
    def move_slider(self):
        if self.stopped:
            return
        elif self.player.state() == QMediaPlayer.PlayingState:
            self.music_slider.setMinimum(0)
            self.music_slider.setMaximum(self.player.duration())
            self.music_slider.setValue(self.player.position())
            current_time = time.strftime('%H:%M:%S', time.gmtime(self.player.position() / 1000))
            song_duration = time.strftime('%H:%M:%S', time.gmtime(self.player.duration() / 1000))
            self.start_time_label.setText(current_time)
            self.end_time_label.setText(song_duration) 
    
    def song_finished(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.next_song()
            
    # Stop Song
    def stop_song(self):
        try:
            self.player.stop()
            self.music_slider.setValue(0)
            self.start_time_label.setText('00:00:00')
            self.end_time_label.setText('00:00:00') 
            self.current_song_name_label.setText(f'Song name goes here')
            self.current_song_path_label.setText(f'Song path goes here')
        except Exception as e:
            print(f"Stopping song error: {e}")

    # Default next: song goes to the next in the queue
    def default_next(self):
        try:
            if self.stackedWidget_2.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().toLocalFile()
                current_song_index = songs.current_song_list.index(current_song_url)
                next_index = (current_song_index + 1) % len(songs.current_song_list)
                current_song = songs.current_song_list[next_index]
                self.song_listWidget.setCurrentRow(next_index)
            elif self.stackedWidget_2.currentIndex() == 1:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().toLocalFile()
                current_song_index = songs.favorites_songs_list.index(current_song_url)
                next_index = (current_song_index + 1) % len(songs.favorites_songs_list)
                current_song = songs.favorites_songs_list[next_index]
                self.favorites_listWidget.setCurrentRow(next_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name_label.setText(f'{os.path.basename(current_song)}')
            self.current_song_path_label.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Default next error: {e}")

    # Next function for self.looped songs
    def looped_next(self):
        try:
            if self.stackedWidget_2.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().toLocalFile()
                current_song_index = songs.current_song_list.index(current_song_url)
                current_song = songs.current_song_list[current_song_index]
                self.song_listWidget.setCurrentRow(current_song_index)
            elif self.stackedWidget_2.currentIndex() == 1:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().toLocalFile()
                current_song_index = songs.favorites_songs_list.index(current_song_url)
                current_song = songs.favorites_songs_list[current_song_index]
                self.favorites_listWidget.setCurrentRow(current_song_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name_label.setText(f'{os.path.basename(current_song)}')
            self.current_song_path_label.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"self.Looped next error: {e}")

    # Next function for shuffled songs
    def shuffled_next(self):
        try:
            if self.stackedWidget_2.currentIndex() == 0:
                song_index = random.randint(0, len(songs.current_song_list) - 1)
                current_song = songs.current_song_list[song_index]
                self.song_listWidget.setCurrentRow(song_index)
            elif self.stackedWidget_2.currentIndex() == 1:
                song_index = random.randint(0, len(songs.favorites_songs_list) - 1)
                current_song = songs.favorites_songs_list[song_index]
                self.favorites_listWidget.setCurrentRow(song_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            self.current_song_name_label.setText(f'{os.path.basename(current_song)}')
            self.current_song_path_label.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Shuffled next error: {e}")

    # Next Song function
    def next_song(self):
        # Determine which list is currently active
        if self.stackedWidget_2.currentIndex() == 0:
            current_list = songs.current_song_list
        else:
            current_list = songs.favorites_songs_list

        # Empty list check
        if not current_list:
            QMessageBox.warning(self.ui, 'No Songs', 'The current playlist is empty.')
            return

        # Playback mode logic
        if self.is_shuffled:
            self.shuffled_next()
        elif self.looped:
            self.looped_next()
        else:
            self.default_next()


    def previous_song(self):
        try:
            if self.looped:
                self.looped_next()
                return
            elif  self.is_shuffled:
                self.shuffled_next()
                return
            
            if self.stackedWidget_2.currentIndex() == 0:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().toLocalFile()
                current_song_index = songs.current_song_list.index(current_song_url)
                previous_index = (current_song_index - 1) % len(songs.current_song_list)
                current_song = songs.current_song_list[previous_index]
                self.song_listWidget.setCurrentRow(previous_index)
            elif self.stackedWidget_2.currentIndex() == 1:
                current_media = self.player.media()
                current_song_url = current_media.canonicalUrl().toLocalFile()
                current_song_index = songs.favorites_songs_list.index(current_song_url)
                previous_index = (current_song_index - 1) % len(songs.favorites_songs_list)
                current_song = songs.favorites_songs_list[previous_index]
                self.favorites_listWidget.setCurrentRow(previous_index)

            song_url = QMediaContent(QUrl.fromLocalFile(current_song))
            self.player.setMedia(song_url)
            self.player.play()
            self.move_slider()

            # Update current song labels
            self.current_song_name_label.setText(f'{os.path.basename(current_song)}')
            self.current_song_path_label.setText(f'{os.path.dirname(current_song)}')
        except Exception as e:
            print(f"Default next error: {e}")

    def favorites_function(self):
        current_index = self.stackedWidget_2.currentIndex()

        if current_index == 0:
            selected_index = self.song_listWidget.currentRow()
            if selected_index < 0:
                NotificationLabel(self.ui, "Select a song to add to favorites", success=False)
                return

            try:
                item = self.song_listWidget.item(selected_index)
                if not item:
                    raise ValueError("Selected item is None.")

                selected_filename = item.text()
                matched_file = next(
                    (f for f in songs.current_song_list if os.path.basename(f).lower() == selected_filename.lower()), None)

                if not matched_file:
                    NotificationLabel(self.ui, "Song Not Found", success=False)
                    return

                if matched_file in songs.favorites_songs_list:
                    NotificationLabel(self.ui, "This song is already in your favorites list.", success=False)
                else:
                    songs.favorites_songs_list.append(matched_file)
                    self.favorites_listWidget.addItem(
                        QListWidgetItem(QIcon('icons/MusicListItem.png'), os.path.basename(matched_file))
                    )
                    NotificationLabel(self.ui, f"{os.path.basename(matched_file)} added to favorites", success=True)

            except Exception as e:
                NotificationLabel(self.ui, f"Unexpected error {str(e)}", success=False)

        elif current_index == 1:
            selected_index = self.favorites_listWidget.currentRow()
            if selected_index < 0:
                NotificationLabel(self.ui, "Select a song to remove from favorites", success=False)
                return

            try:
                item = self.favorites_listWidget.item(selected_index)
                if not item:
                    raise ValueError("Selected item is None.")

                selected_filename = item.text()
                matched_file = next(
                    (f for f in songs.favorites_songs_list if os.path.basename(f).lower() == selected_filename.lower()), None)

                if not matched_file:
                    NotificationLabel(self.ui, "Song Not Found", success=False)
                    return

                songs.favorites_songs_list.remove(matched_file)
                self.favorites_listWidget.takeItem(selected_index)
                NotificationLabel(self.ui, f"{os.path.basename(matched_file)} removed from favorites", success=True)

            except Exception as e:
                NotificationLabel(self.ui, f"Unexpected error {str(e)}", success=False)

    def shuffle_song(self):
        try:
            if not self.is_shuffled:
                self.is_shuffled = True
                self.looped = False
                self.loop_one_btn.setChecked(False)  
            else:
                self.is_shuffled = False
        except Exception as e:
            print(f'Shuffle Song error: {e}')

    def loop_one_song(self):
        try:
            if not self.looped:
                self.looped = True
                self.is_shuffled = False
                self.shuffle_songs_btn.setChecked(False) 
            else:
                self.looped = False
        except Exception as e:
            print(f'Loop One Song error: {e}')

    def remove_selected_song(self):
        list_widget = self.song_listWidget if self.stackedWidget_2.currentIndex() == 0 else self.favorites_listWidget
        song_list = songs.current_song_list if self.stackedWidget_2.currentIndex() == 0 else songs.favorites_songs_list

        current_row = list_widget.currentRow()
        if current_row < 0:
            QMessageBox.information(self.ui, 'Remove Song', 'Please select a song to remove.')
            return

        removed_song = song_list[current_row]
        current_media = self.player.media()
        current_song_url = current_media.canonicalUrl().toLocalFile()

        if os.path.normpath(removed_song) == os.path.normpath(current_song_url):
            QMessageBox.warning(self.ui, 'Cannot Remove', 'You cannot remove the song that is currently playing.')
            return

        reply = QMessageBox.question(
            self.ui, 'Confirm Removal',
            'Are you sure you want to remove the selected song?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            list_widget.takeItem(current_row)
            del song_list[current_row]
        
    def remove_all_songs(self):
        list_widget = self.song_listWidget if self.stackedWidget_2.currentIndex() == 0 else self.favorites_listWidget
        song_list = songs.current_song_list if self.stackedWidget_2.currentIndex() == 0 else songs.favorites_songs_list

        if not song_list:
            QMessageBox.information(self.ui, 'Remove All Songs', 'The playlist is already empty.')
            return

        reply = QMessageBox.question(
            self.ui, 'Confirm Remove All',
            'Are you sure you want to remove all songs from the list?',
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.stop_song()
            list_widget.clear()
            song_list.clear()   
            
    def toggle_mute(self):
        if self.player.volume() == self.current_volume:
            self.player.setVolume(0)
        else:
            self.player.setVolume(self.current_volume)
            
    def switch_to_songlist(self):
        self.stackedWidget_2.setCurrentIndex(0)
        self.label_12.setText('Song List')
        self.add_to_fav_btn.setText('Add to Favorites')
        if len(self.song_listWidget.selectedIndexes()) == 0:
            self.song_listWidget.setCurrentRow(0)

    def switch_to_favorites(self):
        self.stackedWidget_2.setCurrentIndex(1)
        self.label_12.setText('Favorite Songs')
        self.add_to_fav_btn.setText('Remove from Favorites')
        if len(self.favorites_listWidget.selectedIndexes()) == 0:
            self.favorites_listWidget.setCurrentRow(0)

        
        
        
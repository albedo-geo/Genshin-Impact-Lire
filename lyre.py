import mido
from dataclasses import dataclass
from pyautogui import press
import asyncio
import json
from elevate import elevate
import sys


@dataclass
class Note:
    """表示一个要弹奏的音符"""

    note: int
    time: float
    key: str


class MidiLoader:
    def __init__(self, filename: str) -> None:
        self.midi = mido.MidiFile(filename)
        self.load_mapping('mapping.json')

    def load_sheet(self):
        """读取乐谱"""

        def note2key(note: int) -> str:
            n = str(note)
            if n not in self.mapping:
                return ''
            return self.mapping[n]

        sheet = []
        tempo = 500
        for track in self.midi.tracks:
            tick = 0.0
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo // 1000
                elif msg.type == 'note_on':
                    tick += msg.time
                    if msg.velocity > 0:
                        note = Note(msg.note, tick / tempo, note2key(msg.note))
                        sheet.append(note)

        return sheet

    def load_mapping(self, filename: str) -> None:
        """读取音符与按键的对应关系"""
        with open(filename, 'r', encoding='utf-8') as f:
            self.mapping = json.load(f)

    def print_sheet(self) -> None:
        for track in self.midi.tracks:
            res = []
            for msg in track:
                if msg.type == 'note_on' and msg.velocity > 0:
                    res.append(str(msg.note))
            print(' '.join(res))


class LyrePlayer:
    def __init__(self, sheet, speed_modifier=1.0) -> None:
        self.sheet = sheet
        self.speed_modifier = speed_modifier

    def play(self) -> None:
        asyncio.run(self.play_sheet())

    async def play_sheet(self, delay: float = 2.0) -> None:
        """开始演奏"""
        await asyncio.sleep(delay)
        tasks = []
        for note in self.sheet:
            tasks.append(self.wait_and_press(note.key, note.time * self.speed_modifier))
        await asyncio.gather(*tasks)

    async def wait_and_press(self, key: str, delay: float):
        await asyncio.sleep(delay)
        press(key, _pause=False)


if __name__ == '__main__':
    midi = MidiLoader(sys.argv[1])
    sheet = midi.load_sheet()
    player = LyrePlayer(sheet)
    elevate()
    player.play()

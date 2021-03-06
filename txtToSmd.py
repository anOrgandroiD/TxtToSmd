# Requires Python 3.10 to operate

import os
import re
import time
from datetime import date

smdDoc = ''
newFileName = ''
textDoc = ''

def GetFile(fileName, directory):
    for root, dir, files in os.walk(directory):
        if fileName in files: return True
    return False

command = input('Would you like to generate a new smd file or replace an existing one? ').lower()
while(command != 'new' and command != 'replace' and command != 'n' and command != 'r'): command = input('Please enter \'new\' or \'replace\': ')
if(command == 'new' or command == 'n'):
    newFileName = input('What would you like to name your new file? ')
    while len(newFileName) > 15: newFileName = input('Specified name is over 15 characters, enter a new one:')
else:
    smdDoc = input('What is the name of the file you would like to replace? ')
    while(GetFile(smdDoc + '.smd', os.getcwd()) == False): smdDoc = input('That file could not be found, try again: ')
textDoc = input('Which text document would you like to convert to smd? ')
while(GetFile(textDoc + '.txt', os.getcwd()) == False): textDoc = input('That file could not be found, try again: ')

def PauseConstant(pauseConstant):
    switcher = {
        'HALF_NOTE': 96,
        'DOTTED_QUARTER_NOTE': 72,
        'TRIPLET_WHOLE_NOTE': 64,
        'QUARTER_NOTE': 48,
        'DOTTED_EIGHTH_NOTE': 36,
        'TRIPLET_HALF_NOTE': 32,
        'EIGHTH_NOTE': 24,
        'DOTTED_SIXTEENTH_NOTE': 18,
        'TRIPLET_QUARTER_NOTE': 16,
        'SIXTEENTH_NOTE': 12,
        'DOTTED_THIRTY_SECOND_NOTE': 9,
        'TRIPLET_EIGHTH_NOTE': 8,
        'THIRTY_SECOND_NOTE': 6,
        'DOTTED_SIXTY_FOURTH_NOTE': 4,
        'TRIPLET_SIXTEENTH_NOTE': 3,
        'SIXTY_FOURTH_NOTE': 2
    }

    return switcher.get(pauseConstant)

with open(textDoc + '.txt') as i:
    trkCount = 0
    lines = i.readlines()
    lines = [s.replace('\n', '') for s in lines]
    lines = [j for j in lines if j != '']
    regexStartOfTrack = re.compile('StartOfTrack.*')

    def FixedDurationPause(regex, lines):
        newList = list(filter(regex.match, lines))
        for j in newList:
            j = j.strip()
            pauseLength = j[19:-1]
            print('Working on: ' + j)

            switcher = {
                96: '80',
                72: '81',
                64: '82',
                48: '83',
                36: '84',
                32: '85',
                24: '86',
                18: '87',
                16: '88',
                12: '89',
                9: '8a',
                8: '8b',
                6: '8c',
                4: '8d',
                3: '8e',
                2: '8f'
            }

            lines = [s.replace(j, switcher.get(PauseConstant(pauseLength))) for s in lines]
        return lines

    def GetOctaveData(param):
        switcher = {
            '+': 3,
            ' ': 2,
            '-': 1,
            '0': 0
        }

        return switcher.get(param)

    def SingleParameterReplace(hexRep, regexString, lines):
        regex = re.compile(regexString)

        if(regexString == 'FixedDurationPause(.*)'):
            lines = FixedDurationPause(regex, lines)
            return lines

        newList = list(filter(regex.match, lines))
        for j in newList:
            print('Working on: ' + j)
            j = j.strip()
            insertData = hexRep + hex(int(j[len(regexString) - 3:-1].replace(' ', ''), 10))[2:]
            if(len(insertData) == 3): insertData = insertData[0:2] + '0' + insertData[len(insertData) - 1]
            lines = [s.replace(j, insertData) for s in lines]
        return lines

    def MultipleParameterReplace(hexRep, regexString, lines):
        regex = re.compile(regexString)
        newList = list(filter(regex.match, lines))
        for j in newList:
            print('Working on: ' + j)
            j = j.strip()
            hexArray = hex(int(j[len(regexString) - 3:-1].replace(' ', ''), 10))[2:]

            if(len(hexArray) % 2 != 0): unadjustedHex = '0' + hexArray
            else: unadjustedHex = hexArray

            if(len(unadjustedHex) < 3): hexData = '00' + unadjustedHex
            elif(len(unadjustedHex) < 5): hexData = unadjustedHex[-2:] + unadjustedHex[2:-2] + unadjustedHex[:2]
            else: hexData = unadjustedHex[-2:] + unadjustedHex[-4:-2] + unadjustedHex[4:-4] + unadjustedHex[2:4] + unadjustedHex[:2]

            lines = [s.replace(j, hexRep + hexData) for s in lines]
        return lines

    regexNote = re.compile('PlayNote(.*)')
    newList = list(filter(regexNote.match, lines))
    for j in newList:
        print('Working on: ' + j)
        j = j.strip()
        hexNoteData = j[9:-1].replace(' ', '').split(',')
        noteVelocity = hex(int(hexNoteData[0], 10))[2:]
        if len(noteVelocity) < 2: noteVelocity = '0' + noteVelocity

        if(len(hexNoteData) >= 3):
            if not hexNoteData[2].isnumeric:
                tickValue = PauseConstant(hexNoteData[2])
                parameters = 1
            else:
                tickValue = int(hexNoteData[2])
                if(tickValue <= 0): parameters = 0
                elif(tickValue <= 255): parameters = 1
                elif(tickValue <= 65535): parameters = 2
                else: parameters = 3

            if(len(hex(tickValue)[2:]) % 2 == 0): tickBaseHex = '' + hex(tickValue)[2:]
            else: tickBaseHex = '0' + hex(tickValue)[2:]

            if(len(tickBaseHex) < 3): tickHex = '' + tickBaseHex
            else: tickHex = tickBaseHex[-2:] + tickBaseHex[2:-2] + tickBaseHex[:2]
        else:
            parameters = 0
            tickHex = ''

        noteOnly = hexNoteData[1]
        removeThese = '+-0'

        for char in removeThese:
            noteOnly = noteOnly.replace(char, '')

        if len(noteOnly) < 2: hexNoteData[1] = hexNoteData[1][0] + ' ' + hexNoteData[1][1:]
        if len(hexNoteData[1]) < 3: hexNoteData[1] = hexNoteData[1] + ' '

        switcher = {
            'A ': '9',
            'A#': 'a',
            'B ': 'b',
            'C ': '0',
            'C#': '1',
            'D ': '2',
            'D#': '3',
            'E ': '4',
            'F ': '5',
            'F#': '6',
            'G ': '7',
            'G#': '8'
        }

        playedNote = switcher.get(hexNoteData[1][0:2])
        hexNoteData[1].replace(playedNote, '')
        octave = GetOctaveData(hexNoteData[1][2])

        extraneous = hex((parameters * 4) + octave)[2:]
        fullPlayString = '' + noteVelocity + '' + extraneous + playedNote + tickHex
        lines = [s.replace(j, fullPlayString) for s in lines]

    lines = SingleParameterReplace('', 'FixedDurationPause(.*)', lines)
    lines = [s.replace('RepeatLastPause()', '90') for s in lines]
    lines = SingleParameterReplace('91', 'AddToLastPause(.*)', lines)
    lines = SingleParameterReplace('92', 'Pause8Bits(.*)', lines)
    lines = MultipleParameterReplace('93', 'Pause16Bits(.*)', lines)
    lines = MultipleParameterReplace('94', 'Pause24Bits(.*)', lines)
    lines = SingleParameterReplace('95', 'PauseUntilRelease(.*)', lines)
    lines = [s.replace('LoopPoint()', '99') for s in lines]
    lines = SingleParameterReplace('9c', '9C(.*)', lines)
    lines = [s.replace('9D()', '9d') for s in lines]
    lines = [s.replace('9E()', '9e') for s in lines]
    lines = SingleParameterReplace('a0', 'SetTrackOctave(.*)', lines)
    lines = SingleParameterReplace('a1', 'AddToTrackOctave(.*)', lines)
    lines = SingleParameterReplace('a4', 'SetTempo(.*)', lines)
    lines = MultipleParameterReplace('a8', 'A8(.*)', lines)
    lines = SingleParameterReplace('a9', 'A9(.*)', lines)
    lines = SingleParameterReplace('aa', 'AA(.*)', lines)
    lines = [s.replace('SkipNextByte()', 'ab') for s in lines]
    lines = SingleParameterReplace('ac', 'SetProgram(.*)', lines)
    lines = MultipleParameterReplace('af', 'AF(.*)', lines)
    lines = [s.replace('B0()', 'b0') for s in lines]
    lines = SingleParameterReplace('b1', 'B1(.*)', lines)
    lines = SingleParameterReplace('b2', 'B2(.*)', lines)
    lines = SingleParameterReplace('b3', 'B3(.*)', lines)
    lines = MultipleParameterReplace('b4', 'B4(.*)', lines)
    lines = SingleParameterReplace('b5', 'B5(.*)', lines)
    lines = SingleParameterReplace('b6', 'B6(.*)', lines)
    lines = SingleParameterReplace('bc', 'BC(.*)', lines)
    lines = SingleParameterReplace('be', 'BE(.*)', lines)
    lines = SingleParameterReplace('bf', 'BF(.*)', lines)
    lines = SingleParameterReplace('c0', 'C0(.*)', lines)
    lines = SingleParameterReplace('c3', 'C3(.*)', lines)
    lines = [s.replace('SkipNext2Bytes()', 'cb') for s in lines]
    lines = SingleParameterReplace('d0', 'D0(.*)', lines)
    lines = SingleParameterReplace('d1', 'D1(.*)', lines)
    lines = SingleParameterReplace('d2', 'D2(.*)', lines)
    lines = MultipleParameterReplace('d3', 'D3(.*)', lines)
    lines = MultipleParameterReplace('d4', 'D4(.*)', lines)
    lines = MultipleParameterReplace('d5', 'D5(.*)', lines)
    lines = MultipleParameterReplace('d6', 'D6(.*)', lines)
    lines = MultipleParameterReplace('d7', 'PitchBend(.*)', lines)
    lines = MultipleParameterReplace('d8', 'D8(.*)', lines)
    lines = SingleParameterReplace('db', 'DB(.*)', lines)
    lines = SingleParameterReplace('df', 'DF(.*)', lines)
    lines = SingleParameterReplace('e0', 'SetTrackVolume(.*)', lines)
    lines = SingleParameterReplace('e1', 'E1(.*)', lines)
    lines = MultipleParameterReplace('e2', 'E2(.*)', lines)
    lines = SingleParameterReplace('e3', 'SetTrackExpression(.*)', lines)
    lines = MultipleParameterReplace('e4', 'E4(.*)', lines)
    lines = MultipleParameterReplace('e5', 'E5(.*)', lines)
    lines = SingleParameterReplace('e7', 'E7(.*)', lines)
    lines = SingleParameterReplace('e8', 'SetTrackPan(.*)', lines)
    lines = SingleParameterReplace('e9', 'E9(.*)', lines)
    lines = MultipleParameterReplace('ea', 'EA(.*)', lines)
    lines = MultipleParameterReplace('ec', 'EC(.*)', lines)
    lines = MultipleParameterReplace('ed', 'ED(.*)', lines)
    lines = SingleParameterReplace('ef', 'EF(.*)', lines)
    lines = MultipleParameterReplace('f0', 'F0(.*)', lines)
    lines = MultipleParameterReplace('f1', 'F1(.*)', lines)
    lines = MultipleParameterReplace('f2', 'F2(.*)', lines)
    lines = MultipleParameterReplace('f3', 'F3(.*)', lines)
    lines = SingleParameterReplace('f6', 'F6(.*)', lines)

    for j in lines:
        if (regexStartOfTrack.match(j)):
            index1 = lines.index(j)
            index2 = lines.index('EndOfTrack()')
            trkLength = hex(int((len(''.join(lines[index1 + 1:index2])) / 2) + 5))[2:]
            chnlCount = hex(int(j[13:-1], 10))[2:]
            if len(chnlCount) < 2: chnlCount = '0' + chnlCount
            if(len(trkLength) > 8): raise Exception('Track length is too big')
            if(len(trkLength) % 2 != 0): trkLength = '0' + trkLength
            if(len(trkLength) > 2 and len(trkLength) < 7): trkLength = trkLength[-2:] + trkLength[2:-2] + trkLength[:2]
            elif(len(trkLength) >= 7): trkLength = trkLength[-2:] + trkLength[4:-2] + trkLength[2:-4] + trkLength[:2]
            while(len(trkLength) != 8): trkLength += '00'
            lines[index1] = '74726b200000000104ff0000' + trkLength + ('0' if trkCount < 16 else '') + hex(trkCount)[2:] + chnlCount + '0000'
            trkCount += 1
            lines[index2] = '98'
            while(len(''.join(lines[index1:index2 + 1])) % 8 != 0):
                lines[index2] = lines[index2] + '98'

    print('Writing to file...')

    if newFileName == '':
        with open(smdDoc + '.smd', 'rb') as smdFile:
            fileName = smdFile.read().hex()[64:96]
    else:
        fileName = newFileName.upper().encode('utf-8').hex()
        while len(fileName) < 30: fileName = fileName + 'aa'
        fileName += '00'

    year = hex(int(str(date.today())[0:4]))[3:] + '0' + hex(int(str(date.today())[0:4]))[2:3]
    month = '0' + hex(int(str(date.today())[5:7]))[2:]
    day = hex(int(str(date.today())[8:10]))[2:]
    if len(day) < 2: day = '0' + day
    hour = hex(int(str(time.ctime())[11:13]))[2:]
    if len(hour) < 2: hour = '0' + hour
    minute = hex(int(str(time.ctime())[14:16]))[2:]
    if len(minute) < 2: minute = '0' + minute
    second = hex(int(str(time.ctime())[17:19]))[2:]
    if len(second) < 2: second = '0' + second
    currentHexTime = year + month + day + hour + minute + second + '00'
    trkChunks = hex(trkCount)[2:]
    chnlChunks = '{0:#0{1}x}'.format((int(chnlCount, 16) + 1), 4)[2:]
    if len(trkChunks) < 2: trkChunks = '0' + trkChunks

    if len(smdDoc) == 0:
        smdHeader = '736d646c00000000' + '1504' + '0000' + '0000000000000000' + currentHexTime + fileName + '0100000001000000ffffffffffffffff'
    else:
        with open(smdDoc + '.smd', 'rb') as smdFile:
            unkData = smdFile.read().hex()[28:32]
        smdHeader = '736d646c00000000' + '1504' + unkData + '0000000000000000' + currentHexTime + fileName + '0100000001000000ffffffffffffffff'

    songChunk = '736f6e670000000110ff0000b0ffffff0100300001ff' + trkChunks + chnlChunks + '0000000fffffffff00000040004040000002000800ffffffffffffffffffffffffffffffffffffff'
    eocChunk = '656f63200000000104ff000000000000'

    textData = smdHeader + songChunk + ''.join(lines) + eocChunk

    fileLength = hex(int((len(textData) + 8) / 2))[2:]
    if len(fileLength) %2 != 0: fileLength = '0' + fileLength
    if len(fileLength) < 5: fileLength = fileLength[-2:] + fileLength[:2]
    elif len(fileLength) < 7: fileLength = fileLength[-2:] + + fileLength[2:-2] + fileLength[:2]
    else: fileLength = fileLength[-2:] + fileLength[4:-2] + fileLength[2:-4] + fileLength[:2]
    while len(fileLength) != 8: fileLength = fileLength + '00'

    textData = textData[:16] + str(fileLength) + textData[16:]

    hexData = bytes.fromhex(textData)

    if smdDoc != '': writtenSMDDoc = smdDoc
    else:
        writtenSMDDoc = newFileName

    with open(writtenSMDDoc + '.smd', 'wb') as smdFile:
        smdFile.write(hexData)

    generateTextHexFile = input('Would you like the generated hex data to be written in a text file? ')
    if generateTextHexFile.lower() == 'yes' or generateTextHexFile.lower() == 'y':
        with open(textDoc + '_(Hex).txt', 'w') as textFile:
            textFile.write(textData)

    print('Complete!')

    i.close()

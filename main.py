import mido
from mido import Message, MidiFile, MidiTrack
import random as rd
import pandas as pd
import numpy as np

def Average(lst):
    return sum(lst) / len(lst)

def chord_root(prog):
    roots = []
    for i in prog:
        if i == 1:
            roots.append(0)
        elif i == 2:
            roots.append(2)
        elif i == 3:
            roots.append(4)
        elif i == 4:
            roots.append(5)
        elif i == 5:
            roots.append(7)
        elif i == 6:
            roots.append(9)
    return roots

def cpg_any():
    prog = []
    if rd.randrange(0, 2):
        prog.append(1)
        choix = [2, 3, 4, 5, 6]
    else:
        prog.append(6)
        choix = [1, 2, 3, 4, 5]

    rd.shuffle(choix)
    prog = prog + choix[:3]
    return(prog)

def cpg_bridge():
    prog = [1, 2, 3, 4, 5, 6]
    rd.shuffle(prog)
    return(prog[:4])

def cpg(starting_value=0):

    transition_probabilities = np.array([
        [0.0, 0.0869565217391304, 0.0579710144927536, 0.275362318840580, 0.434782608695652, 0.144927536231884],
        [0.180555555555556, 0.0, 0.125000000000000, 0.222222222222222, 0.222222222222222, 0.250000000000000],
        [0.0625000000000000, 0.100000000000000, 0.0, 0.412500000000000, 0.100000000000000, 0.325000000000000],
        [0.397260273972603, 0.0684931506849315, 0.0547945205479452, 0.0, 0.342465753424658, 0.136986301369863],
        [0.269230769230769, 0.0769230769230769, 0.0512820512820513, 0.269230769230769, 0.0, 0.333333333333333],
        [0.164179104477612, 0.0895522388059702, 0.0895522388059702, 0.358208955223881, 0.298507462686567, 0.0]])
    prog = []
    if starting_value == 0:
        starting_value = [1, 6][rd.randrange(0, 2)]
    chain_length = 5
    chain = np.zeros((1, chain_length))
    chain[0][0] = starting_value
    while not (chain[0][0] == chain[0][-1] and (chain[0][0] != chain[0][1] != chain[0][2] != chain[0][3])
                                           and (chain[0][0] != chain[0][2] != chain[0][3] != chain[0][0])
                                           and (chain[0][0] != chain[0][3] != chain[0][0] != chain[0][1])
                                           and (chain[0][1] != chain[0][3] )):
        for i in range(1, chain_length):
            this_step_distribution = transition_probabilities[int(chain[0][i - 1])-1]
            cumulative_distribution = np.cumsum(this_step_distribution)
            r = rd.random()
            chain[0][i] = np.where(cumulative_distribution > r)[0][0]+1
    cp=chain[0][0:4]
    return [int(i) for i in cp]

    return(prog)
# def gen_list_temps(size):
#     list_temps = []
#     somme = 0
#     while(somme < size):
#         if rd.randrange(0,2) == 0:
#             list_temps.append(2)
#             somme = somme+2
#         elif rd.randrange(0,2)==0:
#             list_temps.append(1)
#             somme = somme+1
#         else:
#             newtime = rd.randrange(1,size)
#             if newtime <= size-somme:
#                 list_temps.append(newtime)
#                 somme = somme+newtime
#             else:
#                 list_temps.append(size-somme)
#                 somme = size
#     return list_temps

def gen_list_temps2(size):
    list_temps = []
    somme = 0
    seuilpause = rd.random()-0.1
    seuil2 = seuilpause + rd.random()*(1-seuilpause)+0.2
    seuil1 = seuil2 + rd.random()*(1-seuil2)+0.05

    # seuilpause = 0
    # seuil2 = 0
    # seuil1 = 0.9
    while somme < size:
        if rd.random() < seuilpause:
            newtime = rd.randrange(2,size, 2)
            if newtime <= size-somme:
                list_temps.append(newtime)
                somme = somme+newtime
                print(newtime)
            else:
                list_temps.append(size-somme)
                somme = size
        elif rd.random() < seuil2 and size-somme > 2:
            list_temps.append(2)
            somme = somme+2
        elif rd.random() < seuil1 and size-somme > 1:
            list_temps.append(1)
            somme = somme + 1
        else:
            list_temps.append(0.5)
            list_temps.append(0.5)
            somme = somme+1
    return list_temps, seuilpause, seuil2, seuil1

def bg_compact(liste_binaire):
    liste_compact = []
    count_0 = 0
    for i in reversed(liste_binaire):
        if i == 1:
            liste_compact.insert(0, int(1 + count_0))
            count_0 = 0
        else:
            count_0 += 1
    return liste_compact

def bg_sequence(beat_prob,size):
    sequence = []
    for i in range(size):
        if rd.random() < beat_prob:
            sequence.append(1)
        else:
            sequence.append(0)
    return sequence

def bg_alternate(seq1, seq2):
    seq1_2=[]
    for i in range (len(seq1)):
        seq1_2.append(seq1[i])
        seq1_2.append(seq2[i])
    return seq1_2

def bg_seq_combine(size=4):
    prob1 = rd.random()
    prob2 = rd.random()*prob1
    prob3 = rd.random()*prob2
    print(prob1,prob2,prob3)
    seq1 = bg_sequence(prob1,size)
    seq2 = bg_sequence(prob2,size)
    seq3 = bg_sequence(prob3, 2*size)

    seq1_2 = bg_alternate(seq1,seq2)
    seq1_3_2_3 = bg_alternate(seq1_2,seq3)
    seq1_3_2_3[0]=1
    return bg_compact(seq1_3_2_3)

def arpChord2(root, duration, track):
    root=root-12
    duration=int(duration)
    track.append(Message('control_change', channel=0, control = 64, value=127))

    track.append(Message('note_on', note=root, velocity=rd.randrange(-20,20)+40, time=0))
    track.append(Message('note_off', note=root, velocity=127, time=duration))

    track.append(Message('note_on', note=root+7, velocity=rd.randrange(-20,20)+40, time=0))
    track.append(Message('note_off', note=root+7, velocity=127, time=duration))

    track.append(Message('note_on', note=root+12, velocity=rd.randrange(-20,20)+40, time=0))
    track.append(Message('note_off', note=root+12, velocity=127, time=duration))

    track.append(Message('note_on', note=root+7, velocity=rd.randrange(-20,20)+40, time=0))
    track.append(Message('note_off', note=root+7, velocity=127, time=duration))
    track.append(Message('control_change',channel=0, control = 64, value=0))

def Chord(root, duration, track, list_beat, velocity):
    root=root-12
    #velocity = [1,1,1,1,1,1,1,1]
    chrod_note = [root, root+7, root+12]
    track.append(Message('control_change', channel=0, control = 64, value=127))
    for i in range(len(list_beat)):
        durationtime = int(list_beat[i]/2*duration)
        track.append(Message('note_on', note=root, velocity=velocity[i]*(rd.randrange(-20, 20) + 40), time=0))
        track.append(Message('note_off', note=root, velocity=127, time=durationtime))
        # track.append(Message('note_on', note=root, velocity=rd.randrange(-20, 20) + 40, time=32))
        # track.append(Message('note_off', note=root, velocity=127, time=2))
        # track.append(Message('note_on', note=root, velocity=rd.randrange(-20, 20) + 40, time=32))
        # track.append(Message('note_off', note=root, velocity=127, time=2))
    track.append(Message('control_change', channel=0, control = 64, value=0))

def songbloc (Chord_prog,duree,couplet ):
    notes_possibles = [-36, -34, -32, -31, -29, -27, -25, -24, -22, -20, -19, -17, -15, -13, -12, -10, -8, -7, -5, -3,
                       -1, 0, 2, 4, 5, 7, 9, 11, 12, 14, 16,
                       17, 19, 21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48]
    notepossiblechord = [0, 2, 4, 7, 9, 11, 14, 16, 18, 21, 23, 25, 28, 30, 32, 35, 37, 39]
    list_list_temps = []
    list_prob_pause = []
    list_prob_2 = []
    list_prob_1 = []
    list_prob_05 = []
    for i in range(len(Chord_prog)):
        probs_temps = gen_list_temps2(duree)

        list_prob_pause.append(probs_temps[1])
        list_prob_2.append(probs_temps[2] - probs_temps[1])
        list_prob_1.append(probs_temps[3] - probs_temps[2])
        list_prob_05.append(1 - probs_temps[3])

        list_temps = probs_temps[0]

        if i == 2 or (couplet and i != 0):
            list_list_temps.append(list_list_temps[0])
        else:
            list_list_temps.append(list_temps)

    print(list_prob_pause, list_prob_2, list_prob_1, list_prob_05)
    melodie = []

    derniere_note = 21
    sequance1 = []
    probjump = rd.randrange(1, 7)  ########################################################################
    probautocorr = rd.random()
    probnextchordnote = rd.random()
    dernierchoix = [-1, 0, 1][rd.randrange(0, 3)]
    for i in range(len(Chord_prog)):
        print('chord prog:', i)
        if i == 2 or (couplet and i != 0):
            for j in sequance1:
                melodie.append(notes_possibles[j + Chord_prog[i] - 1])
            derniere_note = sequance1[-1]
        else:
            for j in range(len(list_list_temps[i])):
                if derniere_note <= 0:
                    derniere_note = derniere_note + 1
                if derniere_note >= len(notes_possibles) - 1:
                    derniere_note = derniere_note - 1

                if rd.randrange(0, probjump) == 0:  # or j == 0:
                    print('jump')
                    derniere_note = notepossiblechord[rd.randrange(6, 13)] + Chord_prog[i] - 1
                elif probnextchordnote > rd.random():
                    print('next chord note')
                    if derniere_note - Chord_prog[i] + 1 in notepossiblechord:  # and notepossiblechord[0]<(derniere_note-Chord_prog[i]+1) > notepossiblechord[-1]:
                        derniere_note = notepossiblechord[
                                            notepossiblechord.index(derniere_note - Chord_prog[i] + 1) + [-1, 1][
                                                rd.randrange(0, 2)]] + Chord_prog[i] - 1
                    else:
                        closetnote = min(range(len(notepossiblechord)),
                                         key=lambda l: abs(notepossiblechord[l] - (derniere_note - Chord_prog[i] + 1)))
                        derniere_note = notepossiblechord[closetnote] + Chord_prog[i] - 1

                elif probautocorr > rd.random():
                    print('autocorr')
                    derniere_note = derniere_note + dernierchoix
                else:
                    print('note proche')
                    choix = [-1, 0, 1]
                    dernierchoix = choix[rd.randrange(0, 3)]
                    derniere_note = derniere_note + dernierchoix

                melodie.append(notes_possibles[derniere_note])
                print(melodie)
                if i == 0:
                    sequance1.append(derniere_note - Chord_prog[i] + 1)
                print(derniere_note)
    return (melodie, list_list_temps)


def music(Key= 0, BPM=0,Chord_prog=[0],beat=[0], song_name='new_song.mid', arpeggio=False, duree = 8,instrumentbass=0, instrumentmain=0, probjump=0,probautocorr=0,probnextchordnote=0):
    print(duree)
    if Key == 0:
        Key =rd.randrange(36, 49)
    if BPM == 0:
        BPM =rd.randrange(50, 400)
    tempo = 60000/BPM
    if Chord_prog == [0]:
        Chord_prog = cpg()
    Chord_roots = chord_root(Chord_prog)

    if beat == [0]:
        beat = bg_seq_combine(duree//2)

    if instrumentbass == 0:
        instrumentbass = rd.randrange(0,121)

    if instrumentmain == 0:
        instrumentmain = rd.randrange(0,121)

    if probjump == 0:
        probjump = rd.randrange(1,10)
    if probautocorr == 0:
        probautocorr = rd.random()
    if probnextchordnote == 0:
        probnextchordnote = rd.random()

    print('Chord progression:',Chord_prog,', Key:', Key,', BPM:', BPM, ', Beat:', beat)

    mid = MidiFile()
    track1 = MidiTrack()
    track2 = MidiTrack()
    track3 = MidiTrack()
    track4 = MidiTrack()
    melody = MidiTrack()
    mid.tracks.append(track1)
    mid.tracks.append(track2)
    mid.tracks.append(track3)
    mid.tracks.append(track4)
    mid.tracks.append(melody)


    track1.append(Message('program_change', program=instrumentbass, time=2))
    track2.append(Message('program_change', program=instrumentbass, time=2))
    track3.append(Message('program_change', program=instrumentbass, time=2))
    track4.append(Message('program_change', program=instrumentbass, time=2))
    melody.append(Message('program_change', program=instrumentmain, time=2))

    refrain=songbloc(Chord_prog, duree, couplet=0)
    couplet = songbloc (Chord_prog,duree, couplet=1)
    if Chord_prog[0]== 1:
        bridge_chords = cpg(starting_value=[2, 3, 6][rd.randrange(0, 3)])
    else:
        bridge_chords = cpg(starting_value=[1, 4, 5][rd.randrange(0, 3)])

    bridge = songbloc(bridge_chords,duree/2, couplet=0)

    #### intro (melodie vide)
    melody.append(Message('note_on', note=32, velocity=0, time=0))
    melody.append(Message('note_off', note=32, velocity=127, time=int(4*8*tempo)))
    melodie_tot = couplet[0]+refrain[0]+couplet[0]+refrain[0]+refrain[0]#+bridge[0]+bridge[0]+refrain[0]+refrain[0]
    list_list_temps = couplet[1]+refrain[1]+couplet[1]+refrain[1]+refrain[1]#+bridge[1]+bridge[1]+refrain[1]+refrain[1]
    # melodie_tot = bridge[0]
    # list_list_temps = bridge[1]
    print(melodie_tot)
    loop = 1
    flat_list_temps = []
    for sublist in list_list_temps:
        for item in sublist:
            flat_list_temps.append(item)
    print(flat_list_temps)
    for j in range(loop):
        for i in range(len(flat_list_temps)):
            lanote = Key+12 + melodie_tot[i]
            temps = int(flat_list_temps[i]*tempo)

            melody.append(Message('note_on', note=lanote, velocity=rd.randrange(-20,20)+64, time=0))
            melody.append(Message('note_off', note=lanote, velocity=127, time=temps))

    muted_beat = [[rd.randrange(0,2) for x in range(len(beat))] for y in range(4)]
    random_arpeggio = rd.randrange(0, 3)
    print(muted_beat)


    for x in range(4):
        for i in Chord_roots:
            if arpeggio == True or random_arpeggio==1:
                arpChord2(Key + i, tempo, track1)
                if duree == 8:
                    arpChord2(Key + i, tempo, track1)
            else:
                Chord(Key + i, tempo, track1, beat, velocity=muted_beat[0])
                Chord(Key + i + 7, tempo, track2, beat, velocity=muted_beat[1])
                Chord(Key + i + 12, tempo, track3, beat, velocity=muted_beat[2])

                if i in [0, 5, 7]:
                    Chord(Key + i + 4, tempo, track4, beat, velocity=muted_beat[3])
                else:
                    Chord(Key + i + 3, tempo, track4, beat, velocity=muted_beat[3])


    # for x in range(2):
    #     for i in chord_root(bridge_chords):
    #         if arpeggio == True or random_arpeggio==1:
    #             arpChord2(Key + i, tempo, track1)
    #             if duree//2 == 8:
    #                 arpChord2(Key + i, tempo, track1)
    #         else:
    #             Chord(Key + i, tempo, track1, beat, velocity=muted_beat[0])
    #             Chord(Key + i + 7, tempo, track2, beat, velocity=muted_beat[1])
    #             Chord(Key + i + 12, tempo, track3, beat, velocity=muted_beat[2])
    #
    #             if i in [0, 5, 7]:
    #                 Chord(Key + i + 4, tempo, track4, beat, velocity=muted_beat[3])
    #             else:
    #                 Chord(Key + i + 3, tempo, track4, beat, velocity=muted_beat[3])


    for x in range(3):
        for i in Chord_roots:
            if arpeggio == True or random_arpeggio==1:
                arpChord2(Key + i, tempo, track1)
                if duree == 8:
                    arpChord2(Key + i, tempo, track1)
            else:
                Chord(Key + i, tempo, track1, beat, velocity=muted_beat[0])
                Chord(Key + i + 7, tempo, track2, beat, velocity=muted_beat[1])
                Chord(Key + i + 12, tempo, track3, beat, velocity=muted_beat[2])

                if i in [0, 5, 7]:
                    Chord(Key + i + 4, tempo, track4, beat, velocity=muted_beat[3])
                else:
                    Chord(Key + i + 3, tempo, track4, beat, velocity=muted_beat[3])
    #fin
    #arpChord2(Key + Chord_roots[0], tempo, track1)
    tempo=int(tempo)
    track1.append(Message('note_on', note=Key + Chord_roots[0]-12, velocity=(rd.randrange(-20, 20) + 40), time=0))
    track1.append(Message('note_off', note=Key + Chord_roots[0]-12, velocity=127, time=tempo*4))
    track2.append(Message('note_on', note=Key + Chord_roots[0]+7-12, velocity=(rd.randrange(-20, 20) + 40), time=0))
    track2.append(Message('note_off', note=Key + Chord_roots[0]+7-12, velocity=127, time=tempo*4))
    track3.append(Message('note_on', note=Key + Chord_roots[0], velocity=(rd.randrange(-20, 20) + 40), time=0))
    track3.append(Message('note_off', note=Key + Chord_roots[0], velocity=127, time=tempo*4))
    if Chord_roots[0] in [0, 5, 7]:
        track4.append(Message('note_on', note=Key + Chord_roots[0]+4-12, velocity=(rd.randrange(-20, 20) + 40), time=0))
        track4.append(Message('note_off', note=Key + Chord_roots[0]+4-12, velocity=127, time=tempo * 4))
    else:
        track4.append(Message('note_on', note=Key + Chord_roots[0]+3-12, velocity=(rd.randrange(-20, 20) + 40), time=0))
        track4.append(Message('note_off', note=Key + Chord_roots[0]+3-12, velocity=127, time=tempo * 4))
    attributs = {'Chord_progression': [Chord_prog],
            'Song_name':song_name,
            'Key': Key,
            'BPM': BPM,
            'Beat': [beat],
            'is_arpeggio': arpeggio == True or random_arpeggio==1,
            'Melody': [melodie_tot],
            'Muted_beat': [muted_beat],
            'list_temps': [list_list_temps],
            # 'probability_pause':Average(list_prob_pause),
            # 'probability_2':Average(list_prob_2),
            # 'probability_1':Average(list_prob_1),
            # 'probability_05':Average(list_prob_05),
            'probability_jump': probjump,
            'probability_autocorrelation': probautocorr,
            'probability_next_chord_note': probnextchordnote,
            'instrument_bass':instrumentbass,
            'instrument_main': instrumentmain
            }


    data = pd.DataFrame(attributs, columns=['Chord_progression','Song_name', 'Key', 'BPM', 'Beat', 'is_arpeggio', 'Melody', 'Muted_beat', 'list_temps', 'probability_jump', 'probability_autocorrelation','probability_next_chord_note', 'instrument_bass','instrument_main'])
    #'probability_pause', 'probability_2', 'probability_1', 'probability_05',
    mid.save(song_name)
    return (data)

if __name__ == "__main__":
    songsdata = pd.DataFrame()
    for i in range(20):
        name ='random_'+ str(i+1)+'.mid'
        songdata=music(Chord_prog=[0], beat=[0], song_name=name, Key=0, arpeggio= 0, BPM=0)
        #songdata=music(Chord_prog=[3,6,2,5], beat=[4.0, 1.33333, 2.66666, 2.66666, 1.33333, 4.0], song_name=name,Key=48, arpeggio= 0, BPM=180)
        songsdata=songsdata.append(songdata)

    songsdata.to_csv('songs_data.csv', index = True)

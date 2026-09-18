# -*- coding: utf-8 -*-
"""
playlist.py - Lista de canciones del reproductor.

Para agregar o modificar canciones, edita únicamente esta lista.
Cada canción es un diccionario con cuatro campos:

    title  -> Nombre de la canción (string)
    artist -> Nombre del artista   (string)
    cover  -> Ruta relativa a la portada dentro de apps/music/assets/
             Ejemplo: "covers/mi_portada.jpg"
             Deja "" si no hay portada (se mostrará un placeholder).
    file   -> Ruta relativa al audio dentro de apps/music/assets/
             Ejemplo: "songs/mi_cancion.mp3"
    lyrics -> Letra de la canción (string multilinea).
             Deja "" si no hay letra.

Formatos de audio soportados: mp3, wav, ogg, flac, m4a.
"""

PLAYLIST_NAME = "playlist para tomatito"
PLAYLIST_DESC = "algunas canciones que me recuerdan a ti, otras para que te acuerdes de mi, y otras que simplemente me gustan y quiero compartir contigo:3"

SONGS = [
    {
        "title": "Birthday",
        "artist": "Katy Perry",
        "cover": "covers/1.jpg",
        "file": "songs/Katy Perry - Birthday (SPOTISAVER).mp3",
        "lyrics": "I heard you're feeling\nNothing's going right\nWhy don't you let me stop by?\nThe clock is ticking\nRunning out of time\nSo we should party all night\nSo cover your eyes\nI have a surprise\nI hope you got a healthy appetite\nIf you wanna dance\nIf you want it all\nYou know that I'm the girl that you should call\nBoy, when you're with me\nI'll give you a taste\nMake it like your birthday everyday\nI know you like it sweet\nSo you can have your cake\nGive you something good to celebrate\nSo make a wish\nI'll make it like your birthday everyday\nI'll be your gift\nGive you something good to celebrate\nPop your confetti\nPop your Pérignon\nSo hot and heavy till dawn\nI got you spinning\nLike a disco ball\nAll night they're playing your song\nWe're living the life\nWe're doing it right\nYou're never gonna be unsatisfied\nIf you wanna dance\nIf you want it all\nYou know I'm the girl that you should call\nBoy, when you're with me\nI'll give you a taste\nMake it like your birthday everyday\nI know you like it sweet\nSo you can have your cake\nGive you something good to celebrate\nSo make a wish\nI'll make it like your birthday everyday\nI'll be your gift\nGive you something good to celebrate\nHappy birthday\nSo let me get you in your birthday suit\nIt's time to bring out the big balloons\nSo let me get you in your birthday suit\nIt's time to bring out the big, big, big, big, big, big balloons\nBoy, when you're with me\nI'll give you a taste\nMake it like your birthday everyday\nI know you like it sweet\nSo you can have your cake\nGive you something good to celebrate\nHappy birthday"
    },
    {
        "title": "Danceteria",
        "artist": "Madonna",
        "cover": "covers/2.jpg",
        "file": "songs/Madonna - Danceteria (SPOTISAVER).mp3",
        "lyrics": "Talk about, talk about, talk about\nI get off the train, four, five, six\nWalk to the club, don't wait for shit\nMeet this boy named Martin Burgoyne\nHe's my best friend, he's my boytoy\nWe see the line, it's way too long\nCut to the front, there's Haoui Montaug\nWaves us in, No Entiendes\nI'm not sure you understand this\nWait backstage, get into my car\nDrive to the disco, have a drink at the bar\nPeople, they might talk about us, yeah\nI don't care\nIt's not what I say, it's not what I do\nIt's how my body language talks to you\nI just wanna lose myself in the groove\nGet over here\nEverybody get up and dance\nEveryone here is a work of art\nGet on the elevator, I run into Debi Mazar\nTake us to the third floor\nWalk us to the dance floor\nThen I see Mark Kamins\nHe is a DJ, he's a DJ\nHide the cocaine\nHe played my tape Everybody\nThis is how we start the party\nFace to face, bodies all around\nTemperature is rising and the sweat's dripping down\nEverybody's watching now, oh, yeah\nI don't care\nIt's not what I say, it's not what I do\nIt's how my body language talks to you\nI just wanna lose myself in the groove\nGet over here\nEverybody get up and dance\nEveryone here is a work of art\nThere's Fab Five Freddy and Basquiat\nKeith Haring and Kenny Scharf\nEveryone came from Shafrazi\nSha-fra-zi to the beat\nThere's Maripol and a guy named Fred\nSee these guys spinning on their heads?\nThere's Rock Steady Crew and Crazy Legs\nPuerto Rican boys, they make me crazy\nNile Rodgers and David Byrne\nB-52's had money to burn\nLounge Lizards had so much style\nLower East Side, take a walk on the wild side\nEverybody get up and dance\nEveryone here is a work of art"
    },
    {
        "title": "Push",
        "artist": "Madonna",
        "cover": "covers/3.jpg",
        "file": "songs/Madonna - Push (SPOTISAVER).mp3",
        "lyrics": "You push me to go the extra mile\nYou push me when it's difficult to smile\nYou push me, a better version of myself\nYou push me, only you, and no one else\nYou push me to see the other point of view\nYou push me when there's nothing else to do\nYou push me when I think I know it all\nYou push me when I stumble and I fall\nKeep on pushin', like nobody\nEvery race I win, every mood I'm in\nEverything I do, I owe it all to you\nEvery move I make, every step I take\nEverything I know, it's all because you push me\nYou push me when I don't appreciate\nYou push me not to lie and not to hate\nYou push me when I want it all to end\nYou push me when I really need a friend\nYou push me, all I wanna do is cry\nYou push me when it's time for me to try\nYou push me when I do it for myself\nYou push me, only you, and no one else\nKeep on pushin', like nobody\nEvery race I win, every mood I'm in\nEverything I do, I owe it all to you\nEvery move I make, every step I take\nEverything I do, it's all because you push me\nYou push me"
    },
    {
        "title": "Risk",
        "artist": "Deftones",
        "cover": "covers/4.jpg",
        "file": "songs/Deftones - Risk (SPOTISAVER).mp3",
        "lyrics": "You can't talk\nI'm anxious\nI'm off the walls\nI'm right here just\nCome outside and see it\nBut pack your heart, you might need it\nI'll find a way\nI'm confused some\nBut I think I can try\nI will save your life\nI will save your life\nI'll try for you\nYou're locked up\nYou exhaled\nYou did before\nI've seen it\nCome outside and breathe in\nRelax your arms and let me in\nI'll find a way\nI'm confused some\nBut I think I can try\nI will save your life\nI will save your life\nI'll try for you\nI know what to say to take you\nHigher, higher\nNo one else can take you\nHigher\nBut I'll try\nI'll find a way\nI'm confused some\nBut I think I can try\nI will save your life\nI will save your life\nI'll try for you\nFor you"
    },
    {
        "title": "Be Quiet and Drive (Far Away)",
        "artist": "Deftones",
        "cover": "covers/5.jpg",
        "file": "songs/Deftones - Be Quiet and Drive (Far Away) (SPOTISAVER).mp3",
        "lyrics": "This town don't feel mine\nI'm fast to get away, far\nI dressed you in her clothes\nSo drive me far\nAway\nAway\nAway\nIt feels good to know you're all mine\nNow drive me far\nAway\nAway\nAway\nFar (away)\nI don't care where, just far (away)\nI don't care where, just far (away)\nI don't care where, just far (away)\nI don't care\nFar (away)\nI don't care where, just far (away)\nI don't care where, just far (away)\nI don't care where, just far (away)\nI don't care"
    },
    {
        "title": "Lucy's",
        "artist": "Girlpool",
        "cover": "covers/6.jpg",
        "file": "songs/Girlpool - Lucy's (SPOTISAVER).mp3",
        "lyrics": "An unfamiliar state where you'd rather stay\nA meditation plan when you sway and sink\nI want a fine downtown for the caroler who sounds\nLike quiet when the sun goes down\nI swear I'll be alright although Emily's in the sky\nShe waters the ground with gin she pours me out\nOnto the shadow of her home-state tree\nShe's not ready to let it be\nIn awe with the medals you burned for someone's heart\nA scene I kept dreaming make me swollen then Sharp"
    },
    {
        "title": "Cherry Waves",
        "artist": "Deftones",
        "cover": "covers/7.jpg",
        "file": "songs/Deftones - Cherry Waves (SPOTISAVER).mp3",
        "lyrics": "A sea of waves\nWe hug the same\nPlank (saw your end)\nJust as I'd rehearsed\nOver in my\nBrain (saw your end)\nThe waves suck you in and you drown\nIf like, you should stay down beneath\nI'll swim down, would you?\nYou hang the anchors over my neck (saw your end)\nI liked it at first, but the more you laughed\nThe crazier I came (saw your end)\nThe waves suck you in, then you drown\nIf like, you should sink down beneath\nI'll swim down with you\nIs that what you want?\nYou, is that what you want?\nWave\nWave\nInside\nIf like, you should stay down beneath\nI'll swim down, would you?\nIs that what you want? Would you?\nYou could\nEscape\nBelow\nEscape\nBelow"
    },
    {
        "title": "Fireworks",
        "artist": "Radiator Hospital",
        "cover": "covers/8.jpg",
        "file": "songs/Radiator Hospital - Fireworks (SPOTISAVER).mp3",
        "lyrics": "I've been thinking 'bout that evening, darling\nWe walked further than I thought we would\nYou looked at me like I was your answer\nI looked at you like you meant something\nDo you miss me\nWhy don't you call me\nNo, he's not home\nDid I tell you\nHow I missed you\nI think of you often\nWhen I'm alone\nSpent the evening in my bathrobe, darling\nI tried to wash away the thought of you\nYou've been getting under my skin\nI didn't want this to mean nothin'\nDid you feel them\nFeel the fireworks\nOff on our own\nDid I tell you\nHow I felt them\nI think of them often\nWhen he gets home\nA little spark that don't mean nothin'\nA little spark never hurt no one\nA little spark that don't mean nothin'\nA little spark doesn't mean you're the only one"
    },
    {
        "title": "I Want Someone Badly",
        "artist": "Jeff Buckley, Shudder To Think",
        "cover": "covers/9.jpg",
        "file": "songs/Jeff Buckley, Shudder To Think - I Want Someone Badly (SPOTISAVER).mp3",
        "lyrics": "Now I want someone badly\nGot a girl here tonight\nWants someone new\nSomeone new\nA little cry wants someone badly\nI wanna know if this is a bad lease on me\nI want to know\nI want to know\nAm I sure that I heard you right\nI want to know\nIf you're leaving just do it tonight\nNow I want someone badly\nTo burn in here with me\nBut listen baby\n'Cause I cry all over madly\nDon't do anything do it for/with me\nOh, I wanna know\nAm I sure that I have your love\nI wanna know\nIf you're leaving just make sure it's right\nNow I want someone badly\nCould it be true\nThat someone is you"
    },
    {
        "title": "Overthinking IT",
        "artist": "WILLOW",
        "cover": "covers/10.jpg",
        "file": "songs/WILLOW - Overthinking IT (SPOTISAVER).mp3",
        "lyrics": "Yeah, yeah\nWanna be here, I wanna be there\nI'm overthinking it\nI'ma need to breathe now\nYeah, yeah\nI wanna be here, I wanna be there\nI'm overthinking it\nI'ma need to leave now\nAnd I told you I do\nI told you I do\nI told you I do\nEverything I need\nBut I know that sometimes\nI know that sometimes\nI'm crippled by my mind\nI don't wanna be\nYeah, yeah\nBut I, I have so much work to do\nWork to do, yeah\nAnd I, I have so much love to give\nLove to give\nYou wanna do this, you wanna do that\nYou're overthinking it\nYou just need to sit down\nYeah, yeah\nYou wanna be here, you wanna be there\nOverthinking all the thoughts\nYou just need to chill now\nAnd you told me you do\nYou told me you do\nYou told me you do\nEverything I need\nYeah, yeah\nBut we, we got so much work to do, yeah\nWork to do, yeah\nOh we, we, we got so much love to give, oh\nIf you fall, follow me underground, we can be\nI can be anything that we want\nYou're praying to your God, you're praying to your God\nAfter all, you can be anything that you want\nYou're a queen, I'm a king\nWe, we got so much work to do, yeah\nWe, we, we got such much love to give\nLove to give, yeah"
    },
    {
        "title": "siempreestoypati",
        "artist": "Ed Maverick",
        "cover": "covers/11.jpg",
        "file": "songs/Ed Maverick - siempreestoypati (SPOTISAVER).mp3",
        "lyrics": "Muéstrame tus ojos, déjame ver qué hay en ti\nQuiero verte bien, no quiero verte mal\nQuiero ver tu mirar miel al despertar\nY quisiera ver tu jeta enfrente hablar\nTerminar tomando y luego ir a cenar\nQue me digas: Wey, no empieces a fumar\nEsperar la noche y la ciudad mirar\nImaginar que son luces de Navidad\nSígueme queriendo un chingo y vamos bien\nNadie nos podrá hacer pedos, no es su amor\nQue chinguen a su madre todos ya de una vez\nQue nadie entiende cómo soy\nNadie entiende que es así\nY yo siempre estoy aquí\nY yo siempre estoy pa' ti\nTerminar tomando y luego ir a cenar\nQue me digas: Wey, no empieces a fumar\nEsperar la noche y la ciudad mirar\nImaginar que son luces de Navidad\nY yo siempre estoy pa' ti\nY yo siempre estoy aquí\nY yo siempre estoy pa' ti"
    },
    {
        "title": "Cut Your Bangs",
        "artist": "Girlpool",
        "cover": "covers/12.jpg",
        "file": "songs/Girlpool - Cut Your Bangs (SPOTISAVER).mp3",
        "lyrics": "Last night, I saw your face in the hallowed light\nYou were standing taller than the mountain side\nYour long hair flowed down in blues and whites\nI just stood there, bathed in the quiet\nNo, you say you'll cut your bangs\nI'm calling your bluff\nWhen you lie to me it's in the small stuff\nYou say you'll cut your bangs\nI'm calling your bluff\nWhen you lie to me it's in the small stuff\nNow your mouth is foaming like a rabid dog\nAnd where the river flowed is now a clouded fog\nYour teeth are gnashing louder than your monologue\nAnd I just stood there bathed in the quiet\nNo, you say you'll cut your bangs\nI'm calling your bluff\nWhen you lie to me it's in the small stuff\nNow the flesh is melting off your bones\nThe maggots around your heart make themselves at home\nAnd, where the river flowed I am left alone\nI just stood there, bathed in the quiet\nNo, you say you'll cut your bangs\nI'm calling your bluff\nWhen you lie to me it's in the small stuff"
    },
    {
        "title": "You Can Depend On Me",
        "artist": "Brenda Lee",
        "cover": "covers/13.jpg",
        "file": "songs/Brenda Lee - You Can Depend On Me (SPOTISAVER).mp3",
        "lyrics": "Though you say we're through\nI'll always love you\nAnd you can depend on me\nThough someone that you've met\nHas made you forget\nHoney, you know\nYou can count on me\nWhen I wish, I wish you success\nAnd loads, loads of happiness\nBut baby, I gotta confess\nI'll be lonely\nIf you ever, ahh, if you ever need a friend\nI'll be yours until the end\nAnd you can depend on me\nI wish you success\nAnd loads of happiness\nBut, darling, I gotta confess\nI'm gonna be lonely\nOh if you ever, ahh, if you ever need a friend\nI'll be right by your side ahh, till the end\nAnd you can depend on me\nYou can depend on me"
    },
    {
        "title": "The Grants",
        "artist": "Lana Del Rey",
        "cover": "covers/14.jpg",
        "file": "songs/Lana Del Rey - The Grants (SPOTISAVER).mp3",
        "lyrics": "One, two, ready\nI'm gonna take mine of you with me\nI'm gonna take mine of you with me\nI'm gonna take mine of you with me\nLike Rocky Mountain High\nThe way John Denver sings\nSo you say there's a chance for us\nShould I do a dance for once?\nYou're a family man, but\nDo you think about heaven?\nOh, oh\nDo you think about me?\nMy pastor told me\nWhen you leave, all you take\nIs your memory\nAnd I'm gonna take\nMine of you with me\nSo many mountains too high to climb\nSo many rivers so long, but I'm\nDoin' the hard stuff, I'm doin' my time\nI'm doin' it for us, for our family line\nDo you think about heaven?\nOh, oh\nDo you think about me?\nMy pastor told me\nWhen you leave, all you take\nIs your memories\nAnd I wanna take mine of you with me\nI'm gonna take mine of you with me\nLike Rocky Mountain High\nThe way John Denver sings\nMy sister's first-born child\nI'm gonna take that too with me\nMy grandmother's last smile\nI'm gonna take that too with me\nIt's a beautiful life\nRemember that too for me"
    },
    {
        "title": "LIGHT SHOWER",
        "artist": "Melanie Martinez",
        "cover": "covers/15.jpg",
        "file": "songs/Melanie Martinez - LIGHT SHOWER (SPOTISAVER).mp3",
        "lyrics": "You are the light I've been searchin' for forever\nFeels like, man, I've really never felt the rain\nBuried in the desert, didn't think I'd push through the dirt\nYou just cleansed me like a waterfall, you came\nI'm screamin' like a kettle on a stove\nYou cranked the heat up, I was cold\nMy past grew mold around my heart\nAnd all my anger, sadness, regret disappeared, it's madness\nI'm not used to all this water love, it's true\nBut you made me want to\nPlan out my last days on Earth eating you\nOoh, ooh, ooh\nThe tips of your teeth fit perfect in me\nYou're a shower of light I'd devour\nAny day of the week\nBaby, cleanse me\nI was surprised to see heaven in your eyes\nI never once was treated right, you're what I'm missin' in my life\nAs bright as the Sun, give me your vitamin D\nLet's run into another dimension\nYou make me feel like I'm on drugs\nI'm screamin' like a kettle on a stove\nYou crank the heat up, I was cold\nMy past grew mold around my heart\nAnd all my anger, sadness, regret disappeared, it's madness\nI'm not used to all this water love, it's true\nBut you made me want to\nPlan out my last days on Earth eating you\nOoh, ooh, ooh\nThe tips of your teeth fit perfect in me\nYou're a shower of light I'd devour\nAny day of the week\nBaby, cleanse me"
    },
    {
        "title": "Living Legend",
        "artist": "Lana Del Rey",
        "cover": "covers/16.jpg",
        "file": "songs/Lana Del Rey - Living Legend (SPOTISAVER).mp3",
        "lyrics": "Hmm, oh-oh\nBlackbirds will sing in the same key\nAs you play in the shoes that I bought you\nAnd sweet baby Jane don't know a thing\nAbout my songs, but she knows I'm a monsoon\nAnd, baby, you\nAll the things you do\nAnd the ways you move\nSend me straight to Heaven\nAnd, baby, you\nWhat you never knew\nWhat I never said\nIs you're my living legend\nHipsters will sing just like a dream\nIn Sin-é or the back Brooklyn bayou\nBut you never cared about my name\nAnd, darling, I never meant to defy you\nBut, baby, you\nAll them things you do\nAnd those ways you moved\nSend me straight to Heaven\nAnd, baby you\nI never said to you\nYou really are\nMy living legend\nI got guns in the summertime\nAnd horses, too\nI never meant to be bad or unwell\nI was just living on the edge\nRight between Heaven and Hell\nAnd I'm tired of it\nOh, all the things you do\nAnd the ways you move\nSend me straight to Heaven\nAnd, baby, you\nWhat I never said to you\n'Cause you really are\nMy living legend\nMy living legend\nMy living legend\nMy living legend"
    },
    {
        "title": "My One And Only Love",
        "artist": "Mon Laferte, Natalia Lafourcade, Silvana Estrada",
        "cover": "covers/17.jpg",
        "file": "songs/Mon Laferte, Natalia Lafourcade, Silvana Estrada - My One And Only Love (feat. Natália Lafourcade & Silvana Estrada) (SPOTISAVER).mp3",
        "lyrics": "(Uh-uh-uh-uh)\nMi querido amor\nYo sé, quedaron cicatrices\nHoy será mejor\nYa sabemos de nuestros matices\nAh, ah, yo sé que sanará\nAh, ah, yo sé que sanará\nThere's no reason\nNot to love you like I love you\nReason, we will be alright\nWe won't cry, ah-ah, ah-ah-ah\nCry, ah-ah, we will be alright\nWe won't cry\n(Uh-uh-uh-uh)\nMi querido amor, seremos un lugar seguro\nEl tiempo pasará, tenemos miles de futuros\nAh, ah, yo sé que sanará\nAh, ah, yo sé que sanará\nThere's no reason\nNot to love you like I love you\nReason, we will be alright\nWe won't cry, ah-ah, ah-ah-ah\nAh-ah, ah-ah-ah\n(Uh-uh-uh-uh)\nY, de blanco, te esperé en el altar (ah)\nTú eres lo que siempre yo soñé (uh)\nMy love, my one and only love (uh)\nThere's no reason\nNot to love you like I love you\nReason, we will be alright\nWe won't cry, ah-ah, ah-ah-ah\nAh-ah, tú y yo en cada eternidad"
    },
    {
        "title": "Cherry Blossom",
        "artist": "Lana Del Rey",
        "cover": "covers/18.jpg",
        "file": "songs/Lana Del Rey - Cherry Blossom (SPOTISAVER).mp3",
        "lyrics": "What you don't tell no one, you can tell me\nLittle ghost, tall, tan like milk and honey\nYou're very brave\nAnd very free\nI push you high\nCherry blossom on your sycamore tree\nWhat you don't tell no one, you can tell me\nSwing it high like Jesus, wild and free\nDandelions in your hair, baby\nYou're very brave\nAnd there's much to see\nI push you high\nCherry blossom on your sycamore tree\nWhat you don't tell no one, you can tell me\nAnd when you're scared\nI'll be right here\nYou feel afraid\nMommy is there\nIt's a cruel, cruel world\nBut we don't care\n'Cause what we've got\nWe've got to share\nWhat you don't tell no one, you can tell me\nLittle ghost, blonde hair with lemonade tea\nThere's much to learn\nAnd so much to see\nI push you high\nAngelina, on your sycamore tree\nWhat you don't tell no one, you can tell me"
    },
    {
        "title": "Into Me You See",
        "artist": "Katy Perry",
        "cover": "covers/19.jpg",
        "file": "songs/Katy Perry - Into Me You See (SPOTISAVER).mp3",
        "lyrics": "I built a wall, so high no one could reach\nA life of locks, I swallowed all the keys\nI was petrified, only knew how to hide\nThey can't hurt me, if they don't know me\nA full facade made a mirage out of me\nThen you came and started digging for a treasure underneath\nAnd you found a better version of me I had never seen\nInto me you see, into me you see\nYou broke me wide open, open sesame\nInto me you see, into me you see\nYou got me wide open, now I'm ready\nIs this intimacy?\nI was a ship, floating aimlessly\nSo camouflaged, was my own worst enemy\nThen you came in like a sailor with a heart that anchored me\nAnd every day I wake up grateful I'm no longer lost at sea\nInto me you see, into me you see\nYou broke me wide open, open sesame\nInto me you see, into me you see\nYou got me wide open, now I'm ready\nIs this intimacy?\nOh, 'cause no one's ever seen me like this\nSeen right through the bullshit\nI pray that I can keep unfolding\nPray that I can just stay open\nJust stay open, just stay open, just stay open\nOh, 'cause you broke me wide open, open sesame\nInto me you see, into me you see\nYou got me wide open, now I'm ready\nThis is intimacy"
    },
    {
        "title": "Sweet Carolina",
        "artist": "Lana Del Rey",
        "cover": "covers/20.jpg",
        "file": "songs/Lana Del Rey - Sweet Carolina (SPOTISAVER).mp3",
        "lyrics": "(Okay)\nDon't have to write me a letter\n'Cause I'll always be right here\nCloser to you than your next breath, my dear\nWe love every hair on your head\nLove you like God loves you\nAnd you say that you're scared\nMight be unprepared for havin' the baby blues\nBaby blues\nBaby blues\nIf things ever go wrong\nJust know this is your song and we love you\nYou name your babe Lilac Heaven\nAfter your iPhone 11\nCrypto forever — screams your stupid boyfriend\nFuck you, Kevin\nWe love every freckle you have\nWe love you like God loves you\nIf you're ever stressed out, just dance in the night\nIf you get those baby blues\nBaby blues\nBaby blues\nIf things ever go wrong\nJust know this is your song and we love you\nPink slippers all on the floor\nWoven nets over the door\nIt's as close as we'll get to the dream that they had\nIn the one night sixties, and\nJason is out in the lawn\nAnd he power-washes every time things go wrong\nIf you're stressed out, just know you can dance to your song\n'Cause we got you\nIf you get the blues\nBaby blues\nJust know this is your song\nIt'll live on and on, way past me and you\nIf you get the blues\nBaby blues\nYou've got us, we've got you\nSo there's nothing to lose, and we love you\nSo don't write me a letter\nI'll always be right here\nCloser to you than your next breath, my dear"
    },
    {
        "title": "No Le Regales Tu Corazón",
        "artist": "Mon Laferte",
        "cover": "covers/21.jpg",
        "file": "songs/Mon Laferte - No Le Regales Tu Corazón (SPOTISAVER).mp3",
        "lyrics": "A tus sueños pasados\nHay que darles una oportunidad\nEl milagro es solo un día a la vez\nEn este viaje, quiero sentarme junto a ti\nSi me dejas, yo te puedo acompañar\nNo se rinde mi obstinado corazón\nNo estás vacío\nYo te siento cuando me besas\nExisto en el potencial que hay en ti\nAmor, cómo me gustaría\nQue te vieras como te veo yo\nYo sigo creyendo\nQue mi amor nos puede salvar\nNo le regales tu corazón\nNo le regales tu corazón\nA veces tengo tanto miedo\nTú no eres como él\nNo le regales tu corazón\nNo le regales tu corazón\nA veces tengo tanto miedo\nTú no eres como él\nTú no eres como él\nNo le regales tu corazón\nNo le regales tu corazón\nA veces tengo tanto miedo\nTú no eres como él\nEl milagro es solo un día a la vez\nEl milagro eres tú\nAmor de mi vida\nNunca olvidaré este viaje con nuestro hijo de siete meses\nEn este momento, voy en el ferry hacia Venecia y lloro de felicidad\nEs que te amo tanto\nAmo nuestra amistad\nTambién amo cada parte de ti\nAmo tu pelo, tus músculos, tu humor\nTus dientes de vampiro, tu olor\nEspecialmente cuando no te bañas\nAmo cuando te emocionas\nY se te llenan los ojitos de lágrimas\nAmo tu bondad, tu seguridad\nAmo como comes\nAmo tus pies, tus manos\nTu ombligo, tu cuello\nLo que más amo en la vida es verte sonreír\nCon esa sonrisa linda que haces cuando levantas los hombros\nY pones la cabeza de lado y cierras los ojitos\nLo que más amo en la vida es tu sonrisa\nTe amo tanto\nTe amo tanto\nTe amo tanto"
    },
    {
        "title": "Double Rainbow",
        "artist": "Katy Perry",
        "cover": "covers/22.jpg",
        "file": "songs/Katy Perry - Double Rainbow (SPOTISAVER).mp3",
        "lyrics": "You're a one-of-a-one, a one-of-a-kind\nThat you only find once in a lifetime\nMade to fit like a fingerprint\nA code that clicks open a gold mine\nThey say one man's trash is another man's treasure\nWhen I found you it was all pitter-patter\nSecretly, I hit the lottery\n'Cause you're brighter than all of Northern Lights\nYou speak to me, even in my dreams\nWouldn't let you go for even the highest price\nThey say one man's trash is another girl's treasure\nSo if it's up to me, I'm gonna keep you forever\n'Cause I understand you, we see eye-to-eye\nLike a double rainbow in the sky\nAnd wherever you go, so will I\n'Cause a double rainbow is hard to find\nWas a phenomenon when you came along\nYeah, our chemistry was more than science\nIt was defining, loud like lightning\nIt was striking, you couldn't deny it\nThey say one man's trash is another man's treasure\nThe two of us together make everything glitter\n'Cause I understand you, we see eye-to-eye\nLike a double rainbow in the sky\nAnd wherever you go, so will I\n'Cause a double rainbow is hard to find\nTo the bottom of the sea I'd go to find you\nClimb the highest peak to be right beside you\nEvery step I take I'm keeping you in mind\n'Cause I understand you, we see eye-to-eye\nLike a double rainbow in the sky\nAnd wherever you go, so will I\n'Cause a double rainbow is hard to find\nIt's hard to find\nOh, it's hard to find\nOnce in a lifetime\nOnce in a lifetime"
    },
    {
        "title": "Estoy Llorando De Tanta Belleza",
        "artist": "Mon Laferte",
        "cover": "covers/23.jpg",
        "file": "songs/Mon Laferte - Estoy Llorando De Tanta Belleza (SPOTISAVER).mp3",
        "lyrics": "Mírame\nNo necesito nada ahora que\nEstamos existiendo\nEn un mismo momento\nNo pido nada a cambio, solo que tú seas tú\nMírame\nVoy en caída libre por tu piel\nEs que eres tanta poesía, ah\nQue todo en mí te ansía\nMi vida detenida, estoy perdida en ti\nAbrázame\nQue estoy llorando de tanta belleza\nValoro toda la existencia\nY trato de entender\nEste cuadro de tanta inocencia y toda esta locura\nTe cuidaré\nEn esta vida fuiste valiente\nAdoro así nuestro presente\nCon todo el laberinto\nLo nuestro es como es, no le hace falta nada, oh\nMírame\nSé que tú ves los mares que hay en mí\nY a este par de peces\nQue quieren navegarte\nDe océano en océano desafiando las tormentas\nMírame\nSolo mírame"
    }
]

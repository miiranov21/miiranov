// Месяц 21 (C1): Время и перемены.
(function(){
const M = window.MD_PROGRAM.en.months[20];
M.weeks = [
  {
    t: "Биографии",
    words: [
      ["upbringing", "воспитание (в детстве)", "Апбрингинг"], ["formative", "формирующий (formative years — годы становления)", "фОрмэтив"], ["prodigy", "вундеркинд", "прОдиджи"], ["acclaim", "признание, восторженные отзывы", "эклЭйм"], ["legacy", "наследие", "лЭгэси"],
      ["posthumous", "посмертный", "пОстьюмэс"], ["obscurity", "безвестность", "эбскьЮэрити"], ["rise to prominence", "выдвинуться, стать известным", "райз ту прОминэнс"], ["humble origins", "скромное происхождение", "хамбл Ориджинз"], ["renowned", "прославленный, известный", "ринАунд"],
      ["memoir", "мемуары, воспоминания", "мЭмуа"], ["contemporary", "современник; современный", "кэнтЭмпэрэри"], ["trailblazer", "первопроходец", "трЭйлблэйзэ"], ["accolade", "награда, высшая похвала", "Экэлэйд"], ["biographer", "биограф", "байОгрэфэ"],
      ["chronicle", "описывать (по порядку); хроника", "крОникл"], ["eminent", "выдающийся, видный", "Эминэнт"], ["heyday", "расцвет, лучшие годы", "хЭйдэй"], ["tenacity", "упорство, цепкость", "тинЭсити"], ["against the odds", "вопреки всему, несмотря на все шансы", "эгЭнст зи одз"],
      ["adversity", "невзгоды, трудности", "эдвЁсити"], ["self-taught", "самоучка; самостоятельно выучившийся", "сэлф-тОт"], ["come of age", "достичь совершеннолетия, повзрослеть", "кам ов эйдж"], ["make a name for oneself", "сделать себе имя", "мэйк э нэйм фо уансЭлф"], ["be credited with", "считаться автором (чего-то), ставиться в заслугу", "би крЭдитид уиз"],
      ["reclusive", "нелюдимый, ведущий затворнический образ жизни", "риклУсив"], ["outspoken", "прямолинейный, открыто высказывающийся", "аутспОукэн"], ["pave the way", "проложить путь", "пэйв зэ уэй"], ["enduring", "непреходящий, долговечный", "индьЮэринг"], ["rags to riches", "из грязи в князи (от бедности к богатству)", "рэгз ту рИчиз"]
    ],
    phrases: [["She rose from humble origins to international acclaim.", "Она прошла путь от скромного происхождения до мирового признания."], ["He is best remembered for his work on vaccines.", "Его помнят прежде всего за работу над вакцинами."], ["By the time she was thirty, she had already made a name for herself.", "К тридцати годам она уже сделала себе имя."], ["His legacy lives on in the people he trained.", "Его наследие живёт в людях, которых он обучил."], ["This time next year I'll be working on my memoir.", "В это время в следующем году я буду работать над своими мемуарами."], ["By then, she will have spent half her life abroad.", "К тому времени она проживёт за границей половину жизни."]],
    grammar: {
      title: "Future Perfect и Future Continuous",
      text: "Future Continuous (will be + -ing) описывает действие, которое будет в процессе в определённый момент будущего: This time tomorrow I'll be flying to Lisbon. Его же используют для запланированных, «само собой разумеющихся» событий и для вежливых вопросов о планах: Will you be using the car tonight? звучит мягче, чем Will you use the car? Future Perfect (will have + V3) показывает, что действие завершится к определённому моменту в будущем: By 2030 she will have written five books. Типичные слова-сигналы: by (к), by the time (к тому времени как), by then, in two years' time. Future Perfect Continuous (will have been + -ing) подчёркивает длительность вплоть до момента в будущем: By June I'll have been living here for ten years. Частая ошибка русскоговорящих: после by the time, when, before, until в придаточной части will не ставится: By the time you arrive (а не will arrive), we'll have finished. Не путайте by (к сроку) и until (до, всё время до): I'll have finished by Friday, но I'll be working until Friday. Глаголы состояния (know, own, believe) в Continuous не ставим: By then I'll have known him for twenty years.",
      examples: [["This time next week I'll be lying on a beach.", "В это время на следующей неделе я буду лежать на пляже."], ["By the end of the year, we will have moved to Canada.", "К концу года мы уже переедем в Канаду."], ["Will you be coming to the launch on Friday?", "Ты придёшь на презентацию в пятницу?"], ["By the time you read this, I'll have left the company.", "Когда ты это прочтёшь, я уже уйду из компании."], ["In May she'll have been teaching for twenty years.", "В мае исполнится двадцать лет, как она преподаёт."]],
      quiz: [
        { q: "This time tomorrow I ___ to Berlin. (буду в полёте)", a: ["will be flying", "will have flown", "fly"], c: 0 }, { q: "By 2030 the company ___ its emissions by half. (сократит к 2030)", a: ["will have cut", "will be cutting", "has cut"], c: 0 },
        { q: "By the time you ___, we'll have eaten.", a: ["arrive", "will arrive", "will have arrived"], c: 0 }, { q: "Next June I ___ here for ten years. (подчёркиваем длительность)", a: ["will have been living", "will be living", "have been living"], c: 0 },
        { q: "___ you be using the printer this afternoon? (вежливо о планах)", a: ["Will", "Are", "Have"], c: 0 }, { q: "Don't call at eight: we ___ dinner then.", a: ["will be having", "will have had", "have had"], c: 0 },
        { q: "I'll have finished the report ___ Friday. (к пятнице)", a: ["by", "until", "since"], c: 0 }, { q: "By the end of the course, you ___ over 2,000 new words.", a: ["will have learned", "will be learning", "are learning"], c: 0 }
      ]
    },
    read: {
      title: "Из верфи в центр внимания",
      text: "Few people outside the engineering world had heard of Elena Marsh until last spring, when a biographer's account of her life became an unexpected bestseller. Yet her story deserves every bit of the acclaim it is finally receiving.\n\nMarsh was born in 1931 into a family of humble origins in a northern port town, where her father repaired fishing boats. Her upbringing was strict but unusually liberal in one respect: nobody ever told her that machines were not for girls. She spent her formative years in her father's workshop, and by the age of twelve she could strip down an outboard motor faster than most of the apprentices. She was not a prodigy in the conventional sense; teachers described her as stubborn rather than brilliant. What set her apart was tenacity.\n\nLargely self-taught, she talked her way into a drafting job at a shipyard at seventeen. Her early career was a series of setbacks. Two of her designs were rejected without explanation, and a senior engineer claimed credit for a third. Adversity, however, seems only to have sharpened her. In the 1960s she developed a method for reinforcing steel hulls that is still taught today, although for decades it was credited to the man who had presented it at a conference.\n\nHer contemporaries remember her as outspoken and occasionally impossible. She refused interviews, avoided awards ceremonies and grew increasingly reclusive in later life. When she died in 2009, the obituaries were brief. It was only when her private notebooks were donated to a university archive that her biographer, Tom Reyes, began to piece together the scale of her achievements. The notebooks reveal a trailblazer who quietly paved the way for a generation of women in naval engineering, many of whom never knew her name.\n\nThe book has already prompted a reassessment. Next month a maritime museum will be opening a permanent exhibition devoted to her work, and the engineering institute she once tried to join will award her a posthumous fellowship. Reyes, meanwhile, will be touring schools throughout the autumn, telling students how a girl from a boatyard rose to prominence in a field that did its best to keep her out.\n\nWill her name endure? Reyes is optimistic. 'By the end of this decade,' he says, 'thousands of students will have learned her method and, for once, they'll know who actually invented it. That will have been her real legacy: not the accolades she was denied, but the people she made room for.'\n\nIt is a fitting milestone for a woman who spent most of her life in obscurity, and who, by her own admission, never imagined that anyone would want to read about her.",
      gloss: [["strip down", "разобрать (механизм)"], ["outboard motor", "подвесной лодочный мотор"], ["drafting job", "работа чертёжника"], ["hull", "корпус судна"], ["obituary", "некролог"], ["piece together", "восстановить по частям"], ["reassessment", "переоценка"], ["fellowship", "почётное членство (в научном обществе)"]],
      qs: [
        { q: "What made Marsh stand out early in life, according to the article?", a: ["Her persistence rather than exceptional talent", "Her outstanding results at school", "Her father's connections at the shipyard"], c: 0 },
        { q: "Why was Marsh's contribution overlooked for so long?", a: ["Her key method was attributed to someone else and she avoided publicity", "She published her work under a false name", "Her designs were never actually used"], c: 0 },
        { q: "What triggered the renewed interest in her?", a: ["The discovery of her notebooks and the biography based on them", "A museum exhibition organised before her death", "A conference at which she finally presented her method"], c: 0 },
        { q: "What does Reyes see as her most important legacy?", a: ["Making it possible for others, especially women, to enter the field", "The awards she will receive after her death", "The success of the biography about her"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Nina", "Oliver, you've spent, what, six years on this biography? That's quite a commitment."],
        ["Oliver", "Seven, actually, if you count the research. By the time it comes out in March, I'll have been living with Ray Collins in my head for the best part of a decade."],
        ["Nina", "And for listeners who've never heard of him, who was he?"],
        ["Oliver", "Well, in his heyday, back in the fifties, he was one of the most renowned jazz pianists in Europe. Then, almost overnight, he vanished. He spent the last thirty years of his life running a piano shop in a small town."],
        ["Nina", "Why? Was there some sort of scandal?"],
        ["Oliver", "That's what everyone assumed. But it turns out it was far more ordinary than that. He'd lost the hearing in one ear, and he simply couldn't bear the thought of playing badly in public."],
        ["Nina", "Wow. So he chose obscurity over, I don't know, a slow decline on stage?"],
        ["Oliver", "Exactly. He was a perfectionist, and pretty outspoken about it, too. His contemporaries found him difficult, to put it mildly."],
        ["Nina", "How did you get hold of all this? I gather he never wrote a memoir."],
        ["Oliver", "No, he didn't, which made things tricky. Eventually I tracked down his niece, and she had boxes and boxes of his letters. Honestly, without her, I'd have given up years ago."],
        ["Nina", "And what's next? Are you taking a well-earned break?"],
        ["Oliver", "Ha, not exactly. This time next month I'll be travelling round the country doing readings, and the publisher wants me to record the audiobook as well."],
        ["Nina", "Busy times. Last question: what do you hope readers take away from the book?"],
        ["Oliver", "That a life doesn't have to end in a blaze of glory to matter. He taught hundreds of kids to play in that little shop. That, to me, is his real legacy."]
      ],
      qs: [
        { q: "Why did Ray Collins stop performing?", a: ["He had partly lost his hearing and didn't want to play below his standard", "He was involved in a public scandal", "He wanted to earn more money from his shop"], c: 0 },
        { q: "What does Oliver suggest about Collins's personality?", a: ["He was demanding and not easy to get along with", "He was shy and modest", "He was careless about his music"], c: 0 },
        { q: "Where did Oliver get most of his material?", a: ["From letters kept by Collins's niece", "From Collins's own memoir", "From interviews with Collins himself"], c: 0 },
        { q: "What will Oliver be doing next month?", a: ["Touring the country giving readings", "Taking a long holiday", "Starting work on a new biography"], c: 0 }
      ]
    },
    speak: [
      "By the time this biography is published, I'll have spent nearly seven years researching the life of a forgotten pianist.",
      "This time next month, she'll be travelling around the country, giving talks about her grandfather's remarkable career.",
      "Despite his humble origins, he rose to prominence in his twenties and made a name for himself across Europe.",
      "Her real legacy is not the accolades she received, but the generations of engineers she inspired and quietly encouraged."
    ],
    write: {
      trans: [
        ["Вставь глагол в Future Perfect (finish): By the end of the month, I ___ the first draft.", ["will have finished", "'ll have finished"]],
        ["Вставь глагол в Future Continuous (wait): Don't worry, I ___ for you at the gate.", ["will be waiting", "'ll be waiting"]],
        ["Вставь пропущенное (к тому времени как): ___ she retires, she will have worked here for forty years.", ["By the time"]],
        ["Вставь предлог (стал известен в 1990-х): He rose ___ prominence in the 1990s.", ["to"]]
      ],
      prompt: "Напиши короткую биографию (для сайта или журнала) человека, который тебя вдохновляет: происхождение и воспитание, поворотные моменты, трудности и достижения. В конце порассуждай, что этот человек успеет сделать за ближайшие 10 лет и каким будет его наследие (Future Perfect / Future Continuous).",
      minWords: 200, use: ["upbringing", "setback", "legacy", "will have"],
      model: "My aunt Larisa is not famous, but she is the most remarkable person I know. She was born in a small mining town in the Urals, and her upbringing was anything but easy: her father worked long shifts underground, and her mother raised four children almost single-handedly. Larisa was a curious, stubborn child who taught herself English from old radio broadcasts.\n\nAt twenty-two she moved to Moscow with one suitcase and no contacts. Her first serious setback came two years later, when the translation agency she worked for went bankrupt and she lost all her savings. Instead of going home, she started translating technical manuals on her own, often working through the night. Slowly she made a name for herself as someone who never missed a deadline.\n\nToday she runs a small but respected translation company and trains young translators for free at weekends. She is outspoken, demanding and incredibly generous.\n\nWhat will the next decade bring? By 2035 she will have trained more than two hundred translators, many of whom will be working for international organisations. She will probably still be teaching even then, because she cannot imagine retiring. In my view, her real legacy will not be her company but the confidence she has given to people who, like her, started with nothing."
    }
  },
  {
    t: "Перемены в жизни",
    words: [
      ["uproot", "сорвать с насиженного места", "апрУт"], ["turn over a new leaf", "начать жизнь с чистого листа, исправиться", "тён Оувэ э нью лиф"], ["watershed", "переломный момент, водораздел", "уОтэшэд"], ["upheaval", "потрясение, резкий перелом", "апхИвл"], ["transition", "переход, переходный период", "трэнзИшн"],
      ["settle in", "обжиться, освоиться", "сЭтл ин"], ["clean slate", "чистый лист (начать с нуля)", "клин слэйт"], ["downsize", "переехать в жильё поменьше; сокращать", "даунсАйз"], ["pivotal", "ключевой, решающий", "пИвэтл"], ["irreversible", "необратимый", "ирэвЁсэбл"],
      ["overhaul", "полностью пересмотреть, перестроить", "оувэхОл"], ["daunting", "пугающий (своей сложностью)", "дОнтинг"], ["trepidation", "трепет, тревожное ожидание", "трэпидЭйшн"], ["embrace change", "принимать перемены", "имбрЭйс чэйндж"], ["acclimatise", "акклиматизироваться, привыкнуть", "эклАймэтайз"],
      ["homesickness", "тоска по дому", "хОумсикнэс"], ["leap of faith", "шаг в неизвестность (на веру)", "лип ов фэйс"], ["burn one's bridges", "сжечь мосты", "бён уанз брИджиз"], ["pull up stakes", "сняться с места, переехать", "пул ап стэйкс"], ["disoriented", "растерянный, дезориентированный", "дисОриэнтид"],
      ["bittersweet", "радостный с ноткой грусти", "бИтэсуит"], ["wrench", "тяжёлое расставание, мучительный разрыв", "рэнч"], ["put down roots", "пустить корни", "пут даун рутс"], ["get one's bearings", "сориентироваться, освоиться", "гет уанз бЭарингз"], ["restlessness", "беспокойство, непоседливость", "рЭстлэснэс"],
      ["reinvent oneself", "полностью изменить себя", "риинвЭнт уансэлф"], ["midlife crisis", "кризис среднего возраста", "мИдлайф крайсис"], ["empty nest", "«опустевшее гнездо» (дети выросли и уехали)", "Эмпти нэст"], ["gap year", "год перерыва (в учёбе или работе)", "гэп йиэ"], ["on a whim", "по прихоти, спонтанно", "он э уим"]
    ],
    phrases: [["It was a real turning point in my life.", "Это был настоящий поворотный момент в моей жизни."], ["We finally decided to take the plunge.", "Мы наконец решились."], ["In retrospect, it was the best decision I've ever made.", "Оглядываясь назад, это было лучшее решение в моей жизни."], ["It took me a while to settle in.", "Мне понадобилось время, чтобы обжиться."], ["Leaving my family behind was a real wrench.", "Расставание с семьёй далось мне очень тяжело."], ["I'd been thinking about it for years before I actually did it.", "Я думал об этом годами, прежде чем действительно решился."]],
    grammar: {
      title: "Повествовательные времена: тонкости",
      text: "В рассказе о прошлом у каждого времени своя роль. Past Simple двигает сюжет вперёд: I resigned, sold the flat and bought a ticket. Past Continuous рисует фон или прерванное действие: I was packing when the phone rang. Past Perfect показывает, что одно событие произошло раньше другого: By the time I arrived, the flat had already been sold. Past Perfect Continuous подчёркивает длительность до момента в прошлом и часто объясняет результат: She was exhausted because she had been working twelve-hour shifts. Если порядок событий ясен из контекста или из слов after и before, Past Perfect не обязателен: After I left school, I moved to Riga. «Будущее в прошлом» передают через was going to, was about to и would: I was about to give up when I got the offer. Типичная ошибка русскоговорящих: ставить Past Perfect везде «для солидности»; он нужен только там, где мы возвращаемся назад во времени. В письменной речи для драматизма используют инверсию: Hardly had we arrived when it started to rain; No sooner had I signed the contract than the company was sold (обратите внимание: hardly… when, но no sooner… than).",
      examples: [["I was living in Kazan when I got the job offer.", "Я жил в Казани, когда получил предложение о работе."], ["By the time we moved, we had been saving for five years.", "К моменту переезда мы копили уже пять лет."], ["She had never seen the sea until she moved to Odessa.", "Она ни разу не видела моря, пока не переехала в Одессу."], ["I was about to sign the lease when I changed my mind.", "Я уже собирался подписать договор аренды, как вдруг передумал."], ["No sooner had we settled in than he was transferred again.", "Едва мы обжились, как его снова перевели."]],
      quiz: [
        { q: "I ___ for the bus when I saw the job advert.", a: ["was waiting", "had waited", "have waited"], c: 0 }, { q: "When we got to the flat, the previous tenants ___ out.", a: ["had already moved", "have already moved", "already move"], c: 0 },
        { q: "She was exhausted because she ___ all night. (паковала вещи всю ночь)", a: ["had been packing", "has been packing", "was packed"], c: 0 }, { q: "I ___ to quit, but then they offered me a promotion. (собирался)", a: ["was going", "had gone", "went"], c: 0 },
        { q: "No sooner ___ the contract than the company was sold.", a: ["had I signed", "I had signed", "did I signed"], c: 0 }, { q: "Hardly had we arrived ___ it started to rain.", a: ["when", "than", "then"], c: 0 },
        { q: "We ___ in London for three years before we decided to move back.", a: ["had been living", "have been living", "are living"], c: 0 }, { q: "I ___ about to leave when the phone rang.", a: ["was", "had", "did"], c: 0 }
      ]
    },
    read: {
      title: "Чистый лист в сорок один",
      text: "I had been thinking about leaving for years before I finally took the plunge. The idea would surface every winter, usually in February, when the sky over Novosibirsk had been grey for weeks and the walk to the metro felt like a minor expedition. Then spring would come, and the idea would quietly disappear again.\n\nWhat changed? Nothing dramatic, at least not at first. My daughter had just started university in another city, and the flat suddenly felt enormous. I had been working for the same logistics firm for fourteen years, and I could have done my job in my sleep. One evening, while I was sorting through old paperwork, I found a postcard from Porto that a friend had sent me a decade earlier. I had stuck it on the fridge and then, at some point, forgotten about it. I remember sitting on the kitchen floor holding it and realising that if I didn't go now, I never would.\n\nPeople tend to imagine that a decision like this is a single heroic moment. In my case, it was a slow accumulation of small, slightly embarrassing steps: a Portuguese course I nearly dropped twice, a spreadsheet of rental prices, a conversation with my manager that I rehearsed for a week. No sooner had I handed in my notice than I was overcome by panic. I had burned my bridges, or so it seemed, and I spent several nights wondering whether this was simply a midlife crisis with a plane ticket attached.\n\nThe first months were harder than I had expected. I had prepared for the bureaucracy and the language, but not for the culture shock of small things: shops closing for lunch, neighbours who wanted to chat for twenty minutes, the absence of central heating in a damp Portuguese winter. I felt disoriented and, at times, painfully homesick. Twice I was about to book a flight back.\n\nWhat kept me going was routine. I found a job with a shipping company, joined a hiking group and gradually began to put down roots. By the end of the first year, I had stopped converting every price into roubles in my head, which I now think was the real sign that I had settled in.\n\nIn retrospect, the move was less about Portugal than about permission. For the first time in decades, I allowed myself to be a beginner. It is a daunting feeling at forty-one, but also a strangely liberating one. I am not sure I have reinvented myself, exactly; I still make the same jokes and burn the same toast. But I have stopped waiting for spring to make my decisions for me.",
      gloss: [["surface", "всплывать, появляться"], ["accumulation", "накопление"], ["rehearse", "репетировать"], ["hand in one's notice", "подать заявление об уходе"], ["be overcome by panic", "быть охваченным паникой"], ["damp", "сырой"], ["liberating", "освобождающий"]],
      qs: [
        { q: "What finally prompted the writer to act?", a: ["A combination of an emptier home, a stale job and an old postcard", "A sudden job offer from a company in Porto", "Advice from a friend who lived in Portugal"], c: 0 },
        { q: "How does the writer describe the decision-making process?", a: ["As a gradual series of modest, sometimes awkward steps", "As one sudden moment of great courage", "As a plan organised entirely by a relocation agency"], c: 0 },
        { q: "What did the writer find hardest after the move?", a: ["Small everyday cultural differences", "Dealing with paperwork and officials", "Learning to speak Portuguese"], c: 0 },
        { q: "What does the writer mean by saying the move was 'about permission'?", a: ["It allowed the writer to accept being a beginner again", "The writer needed official permission to work in Portugal", "The writer's family finally agreed to the move"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Ben", "So go on, how did it all happen? Last time we spoke you were adamant you'd never leave London."],
        ["Masha", "I know, I know. I'd been saying that for years. But then the company was restructured, and they gave me a choice: redundancy or a transfer to Toronto."],
        ["Ben", "And you just went for it? Just like that?"],
        ["Masha", "Not exactly. I was about to turn it down, actually. I'd even drafted the email. Then my sister rang and said, 'If you don't go, you'll spend the next ten years wondering.'"],
        ["Ben", "Sisters, eh? They always know which buttons to press."],
        ["Masha", "Tell me about it. Anyway, I took the plunge. Mind you, the first winter nearly finished me off. I'd never experienced minus thirty in my life."],
        ["Ben", "I can imagine. Were you homesick?"],
        ["Masha", "Terribly, for the first few months. What made it worse was that I'd sold my flat, so there was nothing to go back to. It felt like I'd burned all my bridges."],
        ["Ben", "So what was the turning point?"],
        ["Masha", "Oddly enough, it was getting a dog. Suddenly I was out walking every morning, chatting to neighbours, and before I knew it, I'd made friends."],
        ["Ben", "That's brilliant. And now? Any regrets?"],
        ["Masha", "Honestly? Not really. It was a wrench leaving everyone behind, and I still miss proper pubs. But in retrospect, it was exactly the push I needed."],
        ["Ben", "Well, I'm glad it worked out. Maybe I'll come and visit in the summer, when it's not minus thirty."],
        ["Masha", "You'd better. There's a spare room with your name on it."]
      ],
      qs: [
        { q: "Why did Masha have to make a decision about moving?", a: ["Her company was restructured and offered her a transfer or redundancy", "A Canadian company offered her a better job", "Her sister had moved to Toronto and needed help"], c: 0 },
        { q: "What almost stopped her from going?", a: ["She had nearly declined the offer before her sister intervened", "She couldn't find a buyer for her flat", "Her visa application was rejected"], c: 0 },
        { q: "Why did her homesickness feel worse?", a: ["She no longer had a home in London to return to", "She couldn't contact her family", "Her friends refused to visit her"], c: 0 },
        { q: "What helped her settle in?", a: ["Getting a dog, which got her talking to neighbours", "Joining a sports club at work", "Moving to a warmer part of Canada"], c: 0 }
      ]
    },
    speak: [
      "I had been thinking about moving abroad for years before I finally took the plunge and handed in my notice.",
      "No sooner had we settled into our new flat than my husband was offered a job in another country.",
      "In retrospect, losing that job was a turning point, because it forced me to reinvent myself completely.",
      "I was about to give up and book a flight home when I met the people who are now my closest friends."
    ],
    write: {
      trans: [
        ["Вставь глагол в Past Perfect Continuous (live): We ___ in Moscow for ten years before we moved to Berlin.", ["had been living"]],
        ["Вставь пропущенное (собирался позвонить): I ___ to call you, but my phone died.", ["was going", "was about", "had been going"]],
        ["Перефразируй с инверсией: As soon as we arrived, it started to snow. → No sooner ___ arrived than it started to snow.", ["had we"]],
        ["Вставь пропущенное (пустить корни): After years of moving around, we finally decided to put down ___.", ["roots"]]
      ],
      prompt: "Напиши статью для блога о переменах в жизни (своих или знакомого человека): переезд, смена работы, новый этап. Расскажи, что происходило до решения, как всё случилось и что ты понял в итоге. Используй разные повествовательные времена: Past Simple, Past Continuous, Past Perfect, Past Perfect Continuous.",
      minWords: 210, use: ["turning point", "had been", "in retrospect", "settle in"],
      model: "Three years ago, I was working as an accountant in Samara and living what most people would call a comfortable life. I had been doing the same job for nine years, and although I was good at it, I had started to dread Monday mornings.\n\nThe turning point came during a holiday in Georgia. I was sitting in a tiny guesthouse in the mountains when the owner, a retired teacher, asked me what I would do if money were not a problem. I didn't have an answer, and that silence shocked me more than anything she could have said.\n\nWhen I got home, I signed up for an evening course in web design. For a whole year I had been studying at night and working during the day, so by the time I finally handed in my notice, I was exhausted but confident. A small studio in Tbilisi had offered me a junior position, and I accepted before I could change my mind.\n\nIt took me almost six months to settle in. I struggled with the language, missed my friends and twice nearly packed my bags. Gradually, though, the city began to feel like home.\n\nIn retrospect, the move itself was not the hardest part. The hardest part was admitting that the life I had built no longer suited me. Once I had done that, everything else simply followed."
    }
  },
  {
    t: "Воспоминания",
    words: [
      ["reminisce", "предаваться воспоминаниям", "рэминИс"], ["sentimental value", "ценность как память", "сэнтимЭнтл вэлью"], ["vividly", "ярко, живо", "вИвидли"], ["hazy", "смутный, туманный", "хЭйзи"], ["recollection", "воспоминание", "рэкэлЭкшн"],
      ["evoke", "вызывать (чувства, образы)", "ивОук"], ["jog someone's memory", "освежить чью-то память", "джог сАмуанз мЭмэри"], ["ring a bell", "что-то напоминать, звучать знакомо", "ринг э бэл"], ["cherish", "дорожить, бережно хранить", "чЭриш"], ["keepsake", "вещь на память", "кИпсэйк"],
      ["memento", "сувенир на память", "мимЭнтоу"], ["slip one's mind", "вылететь из головы", "слип уанз майнд"], ["fond memories", "тёплые воспоминания", "фонд мЭмэриз"], ["haunt", "любимое (часто посещаемое) место", "хонт"], ["evocative", "навевающий воспоминания, образный", "ивОкэтив"],
      ["in hindsight", "задним умом, оглядываясь назад", "ин хАйндсайт"], ["etched in one's memory", "врезавшийся в память", "эчт ин уанз мЭмэри"], ["conjure up", "вызывать в воображении", "кАнджэр ап"], ["a trip down memory lane", "путешествие в прошлое (в воспоминаниях)", "э трип даун мЭмэри лэйн"], ["reminiscent of", "напоминающий (что-то)", "рэминИснт ов"],
      ["selective memory", "избирательная память", "силЭктив мЭмэри"], ["linger", "задерживаться, не уходить", "лИнгэ"], ["recount", "рассказывать (подробно)", "рикАунт"], ["rose-tinted", "в розовом свете (through rose-tinted glasses)", "рОуз-тинтид"], ["bygone", "минувший, былой", "бАйгон"],
      ["faded", "выцветший, поблёкший", "фЭйдид"], ["heirloom", "семейная реликвия", "Эалум"], ["yearn for", "тосковать по, страстно желать", "йён фо"], ["idyllic", "идиллический", "идИлик"], ["carefree", "беззаботный", "кЭафри"]
    ],
    phrases: [["Does the name ring a bell?", "Это имя тебе о чём-нибудь говорит?"], ["It completely slipped my mind.", "Это совершенно вылетело у меня из головы."], ["That song always brings back memories.", "Эта песня всегда навевает воспоминания."], ["I have fond memories of those summers.", "У меня тёплые воспоминания о тех летних каникулах."], ["Maybe this photo will jog your memory.", "Может, эта фотография освежит твою память."], ["We would spend hours just talking.", "Мы, бывало, часами просто разговаривали."]],
    grammar: {
      title: "would и used to о прошлом",
      text: "Для повторяющихся действий в прошлом, которых больше нет, используют used to и would: When I was a child, we used to / would spend every summer at the dacha. Разница в том, что used to подходит и для действий, и для состояний (I used to live in Omsk; I used to have long hair), а would только для повторяющихся действий: нельзя сказать «I would have a dog» в значении «у меня была собака». Would обычно появляется, когда период уже задан в контексте, и придаёт рассказу ностальгический, слегка литературный оттенок: My grandmother would sit by the window for hours. Для однократного действия не подходит ни то, ни другое: I visited Paris in 2010 (а не used to visit). Отрицание и вопрос строятся с use без -d: I didn't use to…, Did you use to…? Не путайте used to do (раньше делал) с be / get used to doing (привык / привыкаю): I'm used to getting up early. Если указана продолжительность (for ten years), нужен Past Simple: I lived there for ten years, а не used to live there for ten years. Раздражающую привычку в прошлом передают через was always + -ing: He was always losing his keys.",
      examples: [["We used to live in a tiny flat near the station.", "Раньше мы жили в крошечной квартире у вокзала."], ["Every evening my grandfather would tell us stories about the war.", "Каждый вечер дедушка рассказывал нам истории о войне."], ["I didn't use to like olives, but now I love them.", "Раньше я не любил оливки, а теперь обожаю."], ["Did you use to have a nickname at school?", "У тебя в школе было прозвище?"], ["She's used to working nights, so she doesn't mind.", "Она привыкла работать по ночам, так что не против."]],
      quiz: [
        { q: "When I was little, I ___ have a dog called Bim.", a: ["used to", "would", "was used to"], c: 0 }, { q: "Every Sunday, my mother ___ bake a huge apple pie.", a: ["would", "was used to", "is used to"], c: 0 },
        { q: "I didn't ___ like school, but I loved the holidays.", a: ["use to", "used", "using to"], c: 0 }, { q: "We ___ to Sochi in 2005. (один раз)", a: ["went", "used to go", "would go"], c: 0 },
        { q: "Did you ___ live near here?", a: ["use to", "used to", "would to"], c: 0 }, { q: "I've lived in the north for years, so I'm used to ___ the cold.", a: ["dealing with", "deal with", "dealt with"], c: 0 },
        { q: "My brother ___ borrowing my things without asking. It drove me mad.", a: ["was always", "would always to", "used always"], c: 0 }, { q: "My grandparents ___ in that house for forty years.", a: ["lived", "would live", "used to living"], c: 0 }
      ]
    },
    read: {
      title: "Лето, которого, возможно, не было",
      text: "Every family has its mythology, and ours was built around my grandmother's house in a village two hours south of Kyiv. When my cousins and I get together now, usually at weddings or funerals, it takes about ten minutes before someone says, 'Do you remember Baba Olya's cherries?' and we are off on a trip down memory lane.\n\nThe outline of those summers is etched in my memory. We would arrive in early June, pale and restless after the school year, and my grandmother would be waiting at the gate in the same faded blue apron. She used to keep chickens, a bad-tempered goat and, for a few years, a dog that nobody was allowed to name. In the mornings we would be sent to the well with buckets; in the afternoons we would disappear into the fields and come back only when the light began to fade. It was, I would have told you until recently, an idyllic, carefree time.\n\nThen, last winter, I found my mother's letters from those years. She had written to my father, who was working in the north, almost every week, and her version of our summers was rather different. The goat, it turns out, had bitten me so badly that I needed stitches. There was a drought one year, and the cherries I remember so vividly failed completely. My grandmother, whom I recall as endlessly patient, was frequently ill and, my mother wrote, 'exhausted by the children'.\n\nI was shocked at first, then oddly moved. Psychologists have long known that memory is not a recording but a reconstruction. Each time we recall an event, we rebuild it, and in the process we tend to smooth out the rough edges. Researchers even have a name for one part of this: the 'fading affect bias', the tendency for unpleasant emotions linked to a memory to fade faster than pleasant ones. In other words, our rose-tinted view of the past is not so much a failure of memory as a feature of it.\n\nI have not shared the letters with my cousins. Partly this is cowardice, but partly it is a recognition that the summers we remember are real in a different sense. They are the story we tell to keep a bygone world alive, and to keep each other close. My grandmother's house was sold long ago; the cherry trees have presumably been cut down. What lingers is the shared recollection, inaccurate as it may be.\n\nStill, I keep one of the letters in a drawer, alongside a cracked cup that is the only heirloom I inherited from her. Occasionally I read it, not to correct my memories but to remind myself that she was a real person, tired and unwell and doing her best, rather than a character in our family legend. I think she would have preferred that.",
      gloss: [["mythology", "мифология, семейные предания"], ["apron", "фартук"], ["well", "колодец"], ["stitches", "швы (медицинские)"], ["drought", "засуха"], ["fading affect bias", "эффект угасания негативных эмоций"], ["cowardice", "трусость"]],
      qs: [
        { q: "What did the writer discover in the letters?", a: ["That the summers had included real hardships the writer had forgotten", "That the grandmother had never actually owned the house", "That the cousins had invented most of the family stories"], c: 0 },
        { q: "According to the text, why do people tend to remember the past positively?", a: ["Negative feelings attached to memories fade more quickly than positive ones", "People deliberately lie about their childhood", "Unpleasant events are never stored in memory at all"], c: 0 },
        { q: "Why hasn't the writer shown the letters to the cousins?", a: ["Partly out of fear and partly because the shared memories have their own value", "Because the cousins have no interest in the past", "Because the letters were damaged and hard to read"], c: 0 },
        { q: "How does the writer feel about the grandmother at the end?", a: ["Affectionate, with a more realistic understanding of her", "Disappointed and resentful", "Largely indifferent"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Lena", "Oh my goodness, look at this one. Is that you in the sailor suit?"],
        ["Max", "Don't. Mum used to dress me up like that every time we went to see Granddad. I hated it."],
        ["Lena", "You look adorable, though. Where was this taken? It rings a bell, but I can't quite place it."],
        ["Max", "That's the pier at Yalta, surely. We used to go every August, remember? Dad would hire a little boat and pretend he knew how to row."],
        ["Lena", "Oh, yes! And we'd always end up going round in circles while Mum shouted instructions from the shore."],
        ["Max", "Exactly. Funny, I'd completely forgotten about that until now."],
        ["Lena", "What about this one? Who's the woman in the enormous hat?"],
        ["Max", "No idea. Hang on, turn it over, maybe there's something on the back. 'Aunt Vera, 1987.' Nope, still nothing. Does that jog your memory?"],
        ["Lena", "Vaguely. I think she used to send us those awful knitted jumpers for New Year."],
        ["Max", "Oh, her! The jumpers were itchy beyond belief. We'd wear them once, for the photo, and then they'd mysteriously vanish."],
        ["Lena", "It's strange, isn't it? I remember those holidays as endlessly sunny, but Mum says it rained half the time."],
        ["Max", "Well, we were kids. Nobody remembers the rain. We probably just keep the good bits and quietly edit out the rest."],
        ["Lena", "Maybe that's not such a bad thing. Shall we scan these and send them to Mum? She'd love that."],
        ["Max", "Good idea. Just leave out the sailor suit, all right?"]
      ],
      qs: [
        { q: "What did their father use to do on holiday?", a: ["Rent a small boat, although he couldn't row well", "Take them fishing every morning", "Teach them to swim off the pier"], c: 0 },
        { q: "How do they work out who the woman in the hat is?", a: ["From a note on the back of the photo", "Max recognises her immediately", "Their mother tells them on the phone"], c: 0 },
        { q: "What do they remember about Aunt Vera's presents?", a: ["They were uncomfortable jumpers that they hardly ever wore", "They were expensive toys from abroad", "They were books that they still keep"], c: 0 },
        { q: "What point does Max make about childhood memories?", a: ["People tend to keep the pleasant parts and forget the unpleasant ones", "Children remember the weather more accurately than adults", "Photos are less reliable than memories"], c: 0 }
      ]
    },
    speak: [
      "When I was a child, my grandmother would wake us up early and send us to the market for fresh bread.",
      "We used to live in a tiny flat near the river, and the smell of the water still brings back memories.",
      "In hindsight, I probably remember those summers through rose-tinted glasses, because the hard times have simply faded away.",
      "I didn't use to appreciate my parents' stories, but now I'd give anything to hear them recount those years again."
    ],
    write: {
      trans: [
        ["Вставь would или used to (у нас была собака): When I was a child, we ___ have a dog.", ["used to"]],
        ["Вставь отрицательную форму used to: I ___ like reading, but now I can't stop.", ["didn't use to", "did not use to", "never used to"]],
        ["Вставь пропущенное (привык вставать): After ten years in the army, he is used to ___ up at five.", ["getting"]],
        ["Вставь пропущенное (вылетело из головы): Sorry, your birthday completely slipped my ___.", ["mind"]]
      ],
      prompt: "Напиши эссе-воспоминание для литературного конкурса: опиши место или период из детства, которые много для тебя значат. Расскажи, что там обычно происходило (would, used to), какие детали ты помнишь особенно ярко, а какие стёрлись, и как ты смотришь на это время сейчас.",
      minWords: 210, use: ["would", "used to", "vividly", "in hindsight"],
      model: "When I think of my childhood, I think of my grandfather's garage in Tula. It was a cold, cramped building that smelled of petrol and old newspapers, and I used to believe it was the most exciting place in the world.\n\nEvery Saturday morning, my grandfather would collect me from our flat on his ancient motorbike. We would stop at a kiosk for two pirozhki, one with cabbage and one with jam, and then spend the whole day in the garage. He would repair other people's radios while I sorted screws into jars, and occasionally he would let me hold the soldering iron, which felt like an enormous honour.\n\nI remember some details incredibly vividly: the yellow light of the single bulb, the crackle of the radio he always kept on, the way he hummed when a repair was going well. Other things are hazy. I could not tell you what we talked about, or whether it was warm or freezing outside.\n\nIn hindsight, I realise that those Saturdays were not really about radios at all. My parents were going through a difficult divorce, and the garage was the one place where nothing changed. My grandfather never mentioned what was happening at home. He simply gave me a jar of screws and a reason to come back next week. I didn't use to understand how much patience that required, but now I do."
    }
  },
  {
    t: "Повороты карьеры",
    words: [
      ["change tack", "сменить курс, подход", "чэйндж тэк"], ["upskill", "повышать квалификацию", "апскИл"], ["skill set", "набор навыков", "скил сэт"], ["corporate ladder", "корпоративная карьерная лестница", "кОпэрэт лэдэ"], ["stuck in a rut", "застрявший в рутине", "стак ин э рат"],
      ["burn the candle at both ends", "работать на износ", "бён зэ кЭндл эт боус эндз"], ["headhunt", "переманивать (специалиста)", "хЭдхант"], ["redundancy", "сокращение (штата), увольнение по сокращению", "ридАндэнси"], ["severance pay", "выходное пособие", "сЭвэрэнс пэй"], ["portfolio career", "карьера из нескольких параллельных занятий", "портфОулиоу кэриэ"],
      ["calling", "призвание", "кОлинг"], ["fulfilling", "приносящий удовлетворение", "фулфИлинг"], ["cushy job", "тёплое местечко, лёгкая работа", "кУши джоб"], ["step down", "уйти с должности", "стэп даун"], ["climb the ranks", "продвигаться по службе", "клайм зэ рэнкс"],
      ["sideways move", "переход на должность того же уровня", "сАйдуэйз мув"], ["mentorship", "наставничество", "мЭнторшип"], ["on-the-job training", "обучение на рабочем месте", "он-зэ-джОб трэйнинг"], ["entrepreneurial", "предпринимательский", "онтрэпрэнЁриэл"], ["go freelance", "уйти на фриланс", "гоу фрИланс"],
      ["a steep learning curve", "необходимость быстро освоить много нового", "э стип лЁнинг кёв"], ["pay cut", "снижение зарплаты", "пэй кат"], ["golden handcuffs", "«золотые наручники» (выгоды, удерживающие на работе)", "гОулдэн хэндкафс"], ["glass ceiling", "«стеклянный потолок»", "глас сИлинг"], ["hit a plateau", "выйти на плато, застопориться", "хит э плЭтоу"],
      ["jump ship", "уйти (из компании, часто к конкуренту)", "джамп шип"], ["credentials", "квалификация, подтверждённый опыт", "кридЭншлз"], ["weigh the pros and cons", "взвесить все за и против", "уэй зэ проуз энд конз"], ["have second thoughts", "засомневаться, передумывать", "хэв сЭкэнд сотс"], ["side hustle", "подработка, побочный проект", "сайд хАсл"]
    ],
    phrases: [["I'm thinking of changing careers.", "Я подумываю сменить профессию."], ["It was a steep learning curve.", "Пришлось очень быстро осваивать много нового."], ["I took a pay cut, but I've never been happier.", "Я согласился на меньшую зарплату, но никогда не был счастливее."], ["She was headhunted by a rival firm.", "Её переманила конкурирующая фирма."], ["Many of your skills are transferable.", "Многие твои навыки пригодятся и в другой сфере."], ["I felt I had hit a plateau.", "Я чувствовал, что застрял на одном месте."]],
    grammar: {
      title: "Глаголы состояния: оттенки",
      text: "Глаголы состояния (know, believe, own, belong, seem, need, prefer) обычно не употребляются в Continuous: I know him well, а не I'm knowing him. Однако у многих глаголов есть два значения, состояние и действие, и во втором Continuous вполне возможен. Think: I think it's a mistake (мнение), но I'm thinking about changing jobs (процесс обдумывания). Have: I have two degrees (обладание), но I'm having lunch / a hard time (действие, переживание). See: I see what you mean (понимаю), но I'm seeing a career coach (встречаюсь, консультируюсь). Be: He is rude (черта характера), но He's being rude (ведёт себя так сейчас, временно). Taste, smell, look: The soup tastes great (качество), но She's tasting the soup (действие); с feel в значении самочувствия возможны оба варианта: I feel / I'm feeling tired. Love и like иногда ставят в Continuous в разговорной речи, чтобы подчеркнуть яркое временное впечатление: I'm loving my new job! Типичная ошибка русскоговорящих: I'm understanding, I'm wanting вместо I understand, I want; а вот I was wondering if… вполне правильная вежливая формула.",
      examples: [["I think retraining is a smart move.", "Я думаю, переучиться — разумный шаг."], ["I'm thinking of going freelance next year.", "Я подумываю уйти на фриланс в следующем году."], ["She has a lot of experience in sales.", "У неё большой опыт в продажах."], ["We're having a few problems with the new system.", "У нас возникли проблемы с новой системой."], ["You're being very stubborn about this.", "Ты сейчас очень упрямишься."]],
      quiz: [
        { q: "At the moment I ___ about applying for a job in Dubai. (обдумываю)", a: ["am thinking", "think", "thinking"], c: 0 }, { q: "This job ___ more experience than I have. (требует)", a: ["requires", "is requiring", "has been required"], c: 0 },
        { q: "He's normally very friendly, but today he ___ really difficult. (ведёт себя)", a: ["is being", "has being", "does be"], c: 0 }, { q: "I ___ what you mean, but I still disagree.", a: ["see", "am seeing", "have seen"], c: 0 },
        { q: "She ___ a career coach to help her decide what to do next. (сейчас ходит к)", a: ["is seeing", "sees to", "is seen"], c: 0 }, { q: "We ___ some problems with the new manager at the moment.", a: ["are having", "have had been", "having"], c: 0 },
        { q: "This contract ___ to the company, not to you.", a: ["belongs", "is belonging", "belong"], c: 0 }, { q: "I ___ if you could give me some advice about retraining. (вежливо)", a: ["was wondering", "was wonder", "am wondered"], c: 0 }
      ]
    },
    read: {
      title: "Второй акт: «Я хорошо делал свою работу. В этом и была проблема»",
      text: "At thirty-eight, Daniel Brooks was a senior associate at a respected London law firm, with a lucrative salary and a clear path up the career ladder. Today he builds furniture in a converted barn in Somerset. We asked him what happened.\n\nYou had what many people would consider a dream career. Why walk away?\nHonestly, I was good at my job, and that was the problem. I had climbed the ranks quickly, and by my mid-thirties I had hit a plateau. Not professionally: I was still being promoted. But intellectually, I wasn't learning anything. I'd sit in meetings and realise I could predict every sentence before anyone said it.\n\nWas there a particular moment when you decided?\nNot one moment, more a slow burnout. I was working seventy-hour weeks and I was having trouble sleeping. My partner said, 'You're being someone I don't recognise.' That stuck with me. I started doing woodwork at weekends, just to use my hands, and gradually it became more than a hobby.\n\nHow did you make the change in practical terms?\nVery cautiously! I'm not a natural risk-taker. For two years I treated carpentry as a side hustle, selling a few pieces online. Then I did a one-year apprenticeship with a cabinet-maker in Bristol, which meant a huge pay cut. I was by far the oldest person in the workshop.\n\nThat must have been humbling.\nHugely. It was a steep learning curve, and my teacher was not impressed by my law degree. But I discovered that more of my skills were transferable than I'd expected. Drafting a contract and designing a cabinet have something in common: you're thinking about how every part relates to every other part, and what happens if one of them fails.\n\nDo you ever second-guess the decision?\nOf course. Every January, when the orders dry up and the barn is freezing, I wonder what on earth I'm doing. I've given up a lot of job security, and there's a real trade-off: I earn about a third of what I used to. But I don't think I'd go back. The work is fulfilling in a way that law never was for me. At the end of the week I see a table. I can touch it.\n\nWhat advice would you give someone considering a career change?\nDon't jump ship on impulse. Test the idea first, while you still have a salary. And be honest about what you're running away from as well as what you're running towards. Some of my former colleagues who changed careers simply took their unhappiness with them.",
      gloss: [["senior associate", "старший юрист (в юридической фирме)"], ["converted barn", "перестроенный амбар"], ["woodwork", "работа по дереву"], ["cabinet-maker", "столяр-краснодеревщик"], ["humbling", "заставляющий почувствовать себя скромнее"], ["orders dry up", "заказы иссякают"], ["on impulse", "импульсивно, под влиянием момента"]],
      qs: [
        { q: "What was Daniel's main reason for leaving law?", a: ["He no longer felt intellectually challenged", "He had stopped being promoted", "He had been made redundant"], c: 0 },
        { q: "How did Daniel approach the career change?", a: ["Gradually, testing it as a side business before training properly", "By resigning immediately and opening a shop", "By taking a long sabbatical abroad"], c: 0 },
        { q: "What connection does Daniel see between law and carpentry?", a: ["Both involve thinking about how parts fit together and what could go wrong", "Both require working extremely long hours", "Both depend mainly on good relationships with clients"], c: 0 },
        { q: "What warning does he give to others?", a: ["A new career won't help if you bring your old unhappiness with you", "Carpentry is not a profitable profession", "Changing careers after the age of forty is unrealistic"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Helen", "So, Sam, last time you said you were thinking about leaving marketing altogether. Is that still the plan?"],
        ["Sam", "I think so. I mean, I'm fairly sure. I've been in the same role for six years, and frankly, it feels like a dead-end job."],
        ["Helen", "When you say dead-end, what exactly do you mean? No promotions, or no interest?"],
        ["Sam", "Both, really. There's a sort of glass ceiling for anyone who isn't based at head office. And I've stopped caring about the campaigns, which is a bad sign."],
        ["Helen", "Fair enough. What's drawing you towards teaching? You mentioned it in your email."],
        ["Sam", "I've been volunteering at a coding club for teenagers on Saturdays, and I'm absolutely loving it. It's the only time all week that I lose track of time."],
        ["Helen", "That's a great sign. But let's be realistic: retraining as a teacher means a year of study and, initially, quite a drop in salary. How do you feel about that?"],
        ["Sam", "Nervous, to be honest. We've just had a baby, so money's tight. I keep second-guessing myself."],
        ["Helen", "That's completely natural. Have you considered a sideways move first? Some schools hire people from industry to teach computing part-time."],
        ["Sam", "I hadn't, actually. So I could keep some freelance marketing work on the side?"],
        ["Helen", "Exactly. A portfolio career, if you like. It reduces the risk, and you'd find out whether you enjoy teaching five days a week, not just on Saturdays."],
        ["Sam", "That makes a lot of sense. I was seeing it as all or nothing."],
        ["Helen", "Most people do. For next time, I'd like you to look into two or three schools and talk to someone who's made a similar change."],
        ["Sam", "Will do. Thanks, Helen. I'm feeling a lot less stuck already."]
      ],
      qs: [
        { q: "Why does Sam want to leave marketing?", a: ["He has lost interest and sees little chance of promotion", "He has been offered a teaching job", "His company is about to close"], c: 0 },
        { q: "What makes Helen think teaching might suit him?", a: ["He loses track of time when he volunteers with teenagers", "He already has a teaching qualification", "His partner works as a teacher"], c: 0 },
        { q: "What worries Sam most about retraining?", a: ["The financial impact, especially with a new baby", "Being too old to go back to study", "His lack of computer skills"], c: 0 },
        { q: "What does Helen suggest?", a: ["Combining part-time teaching with freelance work to reduce the risk", "Quitting immediately and enrolling on a course", "Staying in marketing and asking for a promotion"], c: 0 }
      ]
    },
    speak: [
      "I'm seriously thinking about retraining, because I feel I've hit a plateau and my skills aren't being used properly.",
      "She was headhunted by a rival firm, but in the end she decided that job security mattered more than money.",
      "Changing careers in your forties involves a real trade-off, and you have to be honest about what you're willing to sacrifice.",
      "He's usually very calm, but he's being unusually defensive today, probably because the restructuring has affected his whole team."
    ],
    write: {
      trans: [
        ["Вставь глагол в нужной форме (think, подумываю): I ___ about going freelance next year.", ["am thinking", "'m thinking"]],
        ["Вставь пропущенное (почему ты ведёшь себя так): Why ___ you being so negative about my plan?", ["are"]],
        ["Вставь пропущенное (её переманили): She was ___ by a competitor last spring.", ["headhunted"]],
        ["Вставь пропущенное (бесперспективная работа): I left because it was a dead-___ job.", ["end"]]
      ],
      prompt: "Напиши мотивационное письмо (cover letter) на вакансию в новой для тебя сфере. Объясни, почему ты меняешь профессию, какие навыки переносятся из прошлого опыта и почему ты готов учиться. Используй хотя бы два глагола состояния в разных значениях (think / be thinking, have / be having, see / be seeing).",
      minWords: 220, use: ["transferable skills", "track record", "retrain", "fulfilling"],
      model: "Dear Ms Patel,\n\nI am writing to apply for the position of Junior UX Researcher advertised on your website. Although my background is in hospital nursing rather than technology, I believe I can bring a valuable perspective to your team.\n\nFor the past eight years I have worked as a nurse in a busy emergency department, and I have a solid track record of staying calm under pressure, communicating with people in distress and noticing small details that others miss. Over time, however, I have become increasingly interested in why patients struggle with the digital systems we use, from appointment apps to self-check-in machines. I see these problems every day, and for some time now I have been thinking about how they could be solved.\n\nLast year I decided to retrain. I completed an online certificate in user experience design and have since carried out two voluntary research projects for a local charity, interviewing elderly people about online banking. I found the work incredibly fulfilling.\n\nI am aware that I have a lot to learn about the technical side of the industry. Nevertheless, I think many of my transferable skills, particularly interviewing, empathy and careful observation, are exactly what good research requires. I am a fast learner and would welcome feedback and mentorship.\n\nThank you for considering my application. I would be delighted to discuss it further at your convenience.\n\nYours sincerely,\nOlga Ivanova"
    }
  }
];
M.exam = {
  read: {
    title: "Миф о большом прорыве",
    text: "Ask successful people how they got where they are, and most will tell you a story with a clear turning point. The actor was spotted in a café; the founder had a brilliant idea in the shower; the novelist was about to give up when a letter arrived from a publisher. These stories are satisfying, which is precisely why we should be suspicious of them.\n\nBiographers have a name for this tendency: the 'retrospective arc'. Looking back, people instinctively select the events that fit a neat narrative and quietly discard the rest. The years of unglamorous effort, the false starts and the sheer luck tend to disappear. What remains is a tidy sequence in which every setback was secretly a lesson and every coincidence was destiny.\n\nTake the case of Maria Lindqvist, a Swedish architect whose career is often cited as an example of sudden success. According to the popular version, she had been working as a waitress when a chance conversation with a customer led to her first commission. When a journalist examined her diaries, however, a more complicated picture emerged. She had been studying architecture part-time for six years. She had entered, and lost, eleven competitions. The famous customer was, in fact, a former teacher who had been following her work for some time. The conversation was real, but it was the last step of a long process rather than the first.\n\nLindqvist herself is amused by the myth. 'I used to tell the café story too,' she admits, 'because it's what people wanted to hear. It's much more fun than \"I worked very hard for a very long time and then something finally worked.\"'\n\nWhy does this matter? Partly because the myth of the big break can be discouraging. If we believe that success arrives in a single dramatic moment, then the long, quiet middle of any project begins to feel like failure. People who are three years into retraining, or building a business, may conclude that they have missed their chance, when in fact they are exactly where most successful people once were.\n\nPsychologists also point out that the stories we tell about our own lives shape our future decisions. Someone who sees their career as a series of lucky accidents may be less inclined to plan; someone who sees it as an unbroken march of achievement may be unprepared for genuine setbacks.\n\nNone of this means we should abandon stories altogether. Narratives help us make sense of change, and a good one can be genuinely motivating. But it is worth telling them more honestly. By the time today's students reach the peak of their careers, they will have heard thousands of tales of overnight success. It would be useful if at least some of those tales mentioned the eleven competitions that came first.",
    gloss: [["discard", "отбрасывать"], ["unglamorous", "будничный, незаметный"], ["false start", "неудачная попытка"], ["commission", "заказ (на проект)"], ["cite", "приводить в пример"], ["unbroken march", "непрерывное шествие"]],
    qs: [
      { q: "What is the main argument of the article?", a: ["Stories of sudden success usually hide long periods of effort and luck", "Most successful people owe everything to a single lucky moment", "Biographers deliberately invent stories about famous people"], c: 0 },
      { q: "What did the journalist find in Lindqvist's diaries?", a: ["Years of study and repeated failures before her first commission", "Proof that she had never worked as a waitress", "Evidence that the customer never existed"], c: 0 },
      { q: "Why did Lindqvist use to tell the café story herself?", a: ["Because it was more entertaining than the truth", "Because she had forgotten what really happened", "Because her publisher insisted on it"], c: 0 },
      { q: "According to the writer, why can the myth be harmful?", a: ["It can make the normal, slow middle stage of a project feel like failure", "It encourages people to work too hard", "It makes people distrust all biographies"], c: 0 },
      { q: "What does the writer conclude?", a: ["We should keep telling stories but make them more honest", "We should stop telling success stories altogether", "Students should ignore stories about successful people"], c: 0 }
    ]
  },
  listen: {
    lines: [
      ["Mark", "Irina? I don't believe it! It must be, what, twenty years?"],
      ["Irina", "Twenty-two, actually. The last time I saw you, you were about to move to Singapore. You'd just got that job with the bank."],
      ["Mark", "Good grief, you remember that? Yes, I was there for almost fifteen years in the end. I used to think I'd never come back."],
      ["Irina", "So what changed your mind?"],
      ["Mark", "My father got ill, and I came home to look after him. It was meant to be temporary, but by the time he'd recovered, I'd got used to being here again. Funny how things work out."],
      ["Irina", "And are you still in banking?"],
      ["Mark", "God, no. I retrained as a furniture restorer, of all things. Everyone thought I'd lost the plot. But I'm loving it. What about you? Are you still teaching?"],
      ["Irina", "Sort of. I'm head of a school now, which means I mostly do paperwork, sadly. But I'm retiring next year. By next September I'll have been working there for thirty years."],
      ["Mark", "Thirty years! That deserves a party. Do you remember the parties we used to have in that awful flat on Kirov Street?"],
      ["Irina", "How could I forget? Your neighbour would bang on the ceiling with a broom every Friday night without fail."],
      ["Mark", "Ha! I'd completely forgotten the broom. So what are you planning to do once you've retired?"],
      ["Irina", "Well, this time next year, if all goes to plan, I'll be walking the Camino de Santiago. I've been promising myself that for ages."],
      ["Mark", "That sounds wonderful. Listen, are you free now? Let's grab a coffee. I want to hear everything."],
      ["Irina", "I'd love that. There's a little place round the corner. And you can tell me how a banker ends up restoring chairs."]
    ],
    qs: [
      { q: "What was happening in Mark's life when they last met?", a: ["He was about to leave for a job in Singapore", "He was living on Kirov Street with his father", "He was retraining as a furniture restorer"], c: 0 },
      { q: "Why did Mark come back home?", a: ["To look after his sick father", "Because he had lost his job at the bank", "Because he wanted to retrain"], c: 0 },
      { q: "How did people react to Mark's career change?", a: ["They thought he had gone mad", "They weren't at all surprised", "They had encouraged him to do it"], c: 0 },
      { q: "What did Mark's neighbour regularly do?", a: ["Bang on the ceiling with a broom on Friday nights", "Complain to the landlord about the noise", "Join their parties uninvited"], c: 0 },
      { q: "What does Irina plan to do after she retires?", a: ["Walk the Camino de Santiago", "Open a new school", "Move to Singapore"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Вставь глагол в Future Perfect Continuous (work): By next September I ___ here for thirty years.", ["will have been working", "'ll have been working"]],
      ["Вставь глагол в Future Continuous (walk): This time next year I ___ across Spain.", ["will be walking", "'ll be walking"]],
      ["Вставь would или used to (у меня были длинные волосы): I ___ have long hair when I was a student.", ["used to"]],
      ["Вставь глагол в Past Perfect (leave): When I got to the station, the train ___ ten minutes earlier.", ["had left"]],
      ["Вставь глагол в нужной форме (think, подумываем): We ___ of selling the flat and moving to the coast.", ["are thinking", "'re thinking"]]
    ],
    prompt: "Напиши эссе (около 250 слов) на тему «Самые важные перемены в жизни мы выбираем не сами». Согласись или не согласись, опираясь на примеры из своей жизни или из биографий известных людей. Расскажи о прошлом (would, used to, повествовательные времена) и порассуждай о будущем (Future Perfect / Future Continuous).",
    minWords: 250, use: ["turning point", "used to", "by the time", "will have"],
    model: "It is often said that the most important changes in our lives are not ones we choose, but ones that happen to us. To a large extent I agree, although I believe that what we do afterwards is very much our own decision.\n\nConsider my own family. My grandfather used to work at a car factory in Togliatti, and for twenty years his life followed the same pattern: he would get up at five, take the same bus and come home exhausted. He had never planned to do anything else. Then, in the early nineties, the factory cut thousands of jobs, and he was suddenly unemployed at fifty. It was a turning point he certainly did not choose. However, by the time I was born, he had opened a small repair shop that later employed six people. The crisis was imposed on him, but the shop was his own creation.\n\nMany well-known biographies follow a similar pattern. Illness, war, redundancy or a chance meeting often triggers the change, yet the person's response determines whether it becomes a disaster or a new beginning.\n\nOf course, some people do make deliberate, carefully planned changes: they retrain, move abroad or leave a secure career for something more fulfilling. These decisions matter, but they are often easier when life has already been shaken up.\n\nLooking ahead, I suspect that my generation will face even more unexpected changes, from automation to climate migration. By the time we retire, many of us will have changed careers several times. We will not choose the circumstances, but we will still be choosing how to respond, and that, in the end, is what shapes a life."
  },
  speak: [
    "By the time I finish this course, I'll have been studying English seriously for almost two years.",
    "When we were children, my father would take us fishing every Sunday, whatever the weather.",
    "I had been working for the same company for over a decade before I finally decided to retrain.",
    "I'm thinking of moving to a smaller town, because I've realised that I don't need such a big flat any more.",
    "In hindsight, losing that job was the best thing that could have happened, although it didn't feel like it at the time."
  ],
  grammar: [
    { q: "By the end of next year, she ___ her PhD.", a: ["will have completed", "will be completing", "completes"], c: 0 }, { q: "When I was young, we ___ live in a village near Pskov.", a: ["used to", "would", "were used to"], c: 0 },
    { q: "I ___ for an hour when the bus finally came.", a: ["had been waiting", "have been waiting", "was waited"], c: 0 }, { q: "This bag ___ to my sister, not to me.", a: ["belongs", "is belonging", "has belonging"], c: 0 },
    { q: "Don't phone me at nine: I ___ my presentation then.", a: ["will be giving", "will have given", "give"], c: 0 }, { q: "No sooner ___ home than the phone rang.", a: ["had I got", "I had got", "did I got"], c: 0 }
  ]
};
})();

// Месяц 3 (A1): Город и прошлое. В конце — экзамен уровня A1 по материалу трёх месяцев.
(function(){
const M = window.MD_PROGRAM.en.months[2];
M.weeks = [
  {
    t: "Город и дорога",
    words: [
      ["street", "улица", "стрит"], ["road", "дорога", "роуд"], ["square", "площадь", "скуэа"], ["bank", "банк", "бэнк"], ["station", "вокзал, станция", "стЭйшн"],
      ["airport", "аэропорт", "Эапорт"], ["museum", "музей", "мьюзИэм"], ["supermarket", "супермаркет", "сУпэмаркит"], ["pharmacy", "аптека", "фАрмэси"], ["hotel", "гостиница", "хоутЭл"],
      ["bus", "автобус", "бас"], ["train", "поезд", "трэйн"], ["taxi", "такси", "тЭкси"], ["car", "машина", "кар"], ["metro", "метро", "мЭтроу"],
      ["ticket", "билет", "тИкит"], ["stop", "остановка, останавливаться", "стоп"], ["map", "карта", "мэп"], ["corner", "угол", "кОрнэр"], ["bridge", "мост", "бридж"],
      ["left", "налево, левый", "лэфт"], ["right", "направо, правый", "райт"], ["straight on", "прямо", "стрэйт он"], ["turn", "поворачивать", "тёрн"], ["cross", "переходить", "крос"],
      ["near", "рядом, близко", "нИэ"], ["far", "далеко", "фар"], ["opposite", "напротив", "Опэзит"], ["between", "между", "битуИн"], ["excuse me", "простите (обращение)", "икскьЮз ми"]
    ],
    phrases: [["Excuse me, where is the station?", "Простите, где вокзал?"], ["Go straight on and turn left.", "Идите прямо и поверните налево."], ["Is it far from here?", "Это далеко отсюда?"], ["It's near the bank.", "Это рядом с банком."], ["How can I get to the museum?", "Как добраться до музея?"], ["A ticket to the centre, please.", "Один билет до центра, пожалуйста."]],
    grammar: {
      title: "Повелительное наклонение и предлоги места",
      text: "Чтобы попросить или объяснить дорогу, берём глагол без to и без подлежащего: Turn left. Go straight on. Запрет — Don't: Don't cross here. Где находится: near — рядом, opposite — напротив, between — между (двумя), next to — рядом с, on the corner — на углу, on the left / on the right — слева / справа.",
      examples: [["Turn right at the bank.", "Поверните направо у банка."], ["Don't take a taxi.", "Не берите такси."], ["The pharmacy is opposite the hotel.", "Аптека напротив гостиницы."], ["The bank is between the shop and the café.", "Банк между магазином и кафе."]],
      quiz: [
        { q: "___ left at the corner.", a: ["Turn", "Turns", "To turn"], c: 0 }, { q: "___ cross the road here!", a: ["Don't", "Not", "No"], c: 0 },
        { q: "The café is ___ the bank and the shop.", a: ["between", "opposite", "near to"], c: 0 }, { q: "The hotel is ___ the station. (напротив)", a: ["opposite", "between", "under"], c: 0 },
        { q: "Is the museum ___ from here?", a: ["far", "near to", "opposite"], c: 0 }, { q: "Go straight ___.", a: ["on", "in", "at"], c: 0 },
        { q: "The pharmacy is ___ the corner.", a: ["on", "in", "between"], c: 0 }, { q: "___ me, where is the metro?", a: ["Excuse", "Sorry to", "Please"], c: 0 }
      ]
    },
    read: {
      title: "Добро пожаловать в наш город",
      text: "Welcome to our town! Our hotel is in Green Street, opposite the park. To get to the old town, go straight on and cross the bridge. The museum is on the left, next to a big square. Don't take a taxi: it's only ten minutes on foot. The station is far, so take bus number five. The bus stop is on the corner, between the bank and the pharmacy. Buy a ticket from the driver.",
      gloss: [["town", "город (небольшой)"], ["old town", "старый город"], ["on foot", "пешком"], ["only", "только"], ["from the driver", "у водителя"]],
      qs: [
        { q: "Где находится отель?", a: ["Напротив парка", "У вокзала", "На площади"], c: 0 },
        { q: "Где музей?", a: ["Слева, рядом с большой площадью", "Справа от моста", "У вокзала"], c: 0 },
        { q: "Как добраться до вокзала?", a: ["На автобусе номер 5", "Пешком", "На такси"], c: 0 },
        { q: "Где остановка автобуса?", a: ["На углу, между банком и аптекой", "У отеля", "У музея"], c: 0 }
      ]
    },
    listen: {
      lines: [["Tourist", "Excuse me, how can I get to the airport?"], ["Man", "Take the metro to Central Station, then take the train."], ["Tourist", "Is the metro near here?"], ["Man", "Yes, go straight on and turn right. It's opposite the supermarket."], ["Tourist", "How much is a ticket?"], ["Man", "About two pounds."], ["Tourist", "Thank you very much!"], ["Man", "You're welcome."]],
      qs: [
        { q: "Куда хочет попасть турист?", a: ["В аэропорт", "На вокзал", "В супермаркет"], c: 0 },
        { q: "Как туда добраться?", a: ["На метро, потом на поезде", "На автобусе", "На такси"], c: 0 },
        { q: "Где метро?", a: ["Напротив супермаркета", "Рядом с банком", "Далеко отсюда"], c: 0 },
        { q: "Сколько стоит билет на метро?", a: ["Около 2 фунтов", "10 фунтов", "20 фунтов"], c: 0 }
      ]
    },
    speak: ["Excuse me, where is the station?", "Go straight on and turn left.", "Is it far from here?", "How can I get to the museum?"],
    write: {
      trans: [["Поверни направо у банка.", ["Turn right at the bank"]], ["Аптека напротив отеля.", ["The pharmacy is opposite the hotel"]], ["Это далеко отсюда?", ["Is it far from here", "Is it far"]], ["Не бери такси.", ["Don't take a taxi"]]],
      prompt: "Объясни другу, как дойти от твоего дома до магазина или метро: куда идти, где повернуть, что находится рядом.",
      minWords: 35, use: ["turn", "straight on", "opposite", "near"],
      model: "Go out of my house and turn left. Go straight on for five minutes. Cross the road at the bank. The metro is on the corner, opposite the supermarket. The pharmacy is near the metro."
    }
  },
  {
    t: "Сейчас: одежда и погода",
    words: [
      ["clothes", "одежда", "клоуз"], ["shirt", "рубашка", "шёрт"], ["T-shirt", "футболка", "тИ-шёрт"], ["trousers", "брюки", "трАузэрз"], ["jeans", "джинсы", "джинз"],
      ["dress", "платье", "дрэс"], ["skirt", "юбка", "скёрт"], ["jacket", "куртка, пиджак", "джЭкит"], ["shoes", "туфли, обувь", "шуз"], ["hat", "шапка, шляпа", "хэт"],
      ["coat", "пальто", "коут"], ["boots", "ботинки, сапоги", "бутс"], ["wear", "носить (одежду)", "уэа"], ["put on", "надевать", "пут он"], ["colour", "цвет", "кАлэ"],
      ["red", "красный", "рэд"], ["blue", "синий", "блу"], ["black", "чёрный", "блэк"], ["white", "белый", "уайт"], ["green", "зелёный", "грин"],
      ["weather", "погода", "уЭзэр"], ["sun", "солнце", "сан"], ["rain", "дождь, идёт дождь", "рэйн"], ["snow", "снег, идёт снег", "сноу"], ["wind", "ветер", "уинд"],
      ["cold", "холодный", "коулд"], ["hot", "жаркий, горячий", "хот"], ["warm", "тёплый", "уом"], ["sunny", "солнечный", "сАни"], ["cloudy", "облачный", "клАуди"]
    ],
    phrases: [["What are you doing?", "Что ты делаешь?"], ["I'm waiting for the bus.", "Я жду автобус."], ["It's raining now.", "Сейчас идёт дождь."], ["What's the weather like?", "Какая погода?"], ["Put on your coat!", "Надень пальто!"], ["She's wearing a red dress.", "На ней красное платье."]],
    grammar: {
      title: "Present Continuous: что происходит прямо сейчас",
      text: "Чтобы сказать, что действие идёт сейчас, используем am / is / are + глагол с -ing: I am reading — Я (сейчас) читаю. Отрицание: I'm not reading, she isn't working. Вопрос: Are you working? What are you doing? Сравни: I work every day (обычно, Present Simple) — I am working now (сейчас). Написание: make → making, swim → swimming, sit → sitting.",
      examples: [["I am reading now.", "Я сейчас читаю."], ["She is wearing a blue dress.", "На ней синее платье."], ["It isn't raining today.", "Сегодня нет дождя."], ["Are they watching TV?", "Они смотрят телевизор?"]],
      quiz: [
        { q: "Look! It ___.", a: ["is snowing", "snows", "snow"], c: 0 }, { q: "I ___ a book now.", a: ["am reading", "read", "reading"], c: 0 },
        { q: "What ___ you doing?", a: ["are", "do", "is"], c: 0 }, { q: "She ___ jeans today.", a: ["is wearing", "wears", "wear"], c: 0 },
        { q: "They ___ watching TV. (не)", a: ["aren't", "don't", "isn't"], c: 0 }, { q: "I usually ___ to work, but today I'm taking a taxi.", a: ["walk", "am walking", "walking"], c: 0 },
        { q: "We ___ swimming in the sea!", a: ["are", "is", "do"], c: 0 }, { q: "___ it raining?", a: ["Is", "Does", "Are"], c: 0 }
      ]
    },
    read: {
      title: "Сообщение из Лондона",
      text: "Hi Mum! I'm writing from London. The weather is terrible: it's cold and it's raining. I'm wearing my warm jacket and boots. Now I'm sitting in a nice café near the river and drinking hot tea. Tom isn't here — he's buying presents for you in a big shop. We hope for sun tomorrow! Love, Ann.",
      gloss: [["terrible", "ужасный"], ["sit", "сидеть"], ["river", "река"], ["presents", "подарки"], ["hope", "надеяться"]],
      qs: [
        { q: "Какая погода в Лондоне?", a: ["Холодно и дождь", "Солнечно", "Идёт снег"], c: 0 },
        { q: "Что надето на Энн?", a: ["Тёплая куртка и ботинки", "Платье", "Пальто и шапка"], c: 0 },
        { q: "Что она делает сейчас?", a: ["Сидит в кафе и пьёт чай", "Гуляет у реки", "Покупает подарки"], c: 0 },
        { q: "Где Том?", a: ["Покупает подарки в магазине", "Сидит с ней в кафе", "В гостинице"], c: 0 }
      ]
    },
    listen: {
      lines: [["Liz", "Hi, where are you?"], ["Mark", "I'm at the bus stop. I'm waiting for the bus."], ["Liz", "Is it cold there?"], ["Mark", "Yes, it's snowing! I'm wearing my big coat and a hat."], ["Liz", "Here it's sunny and warm. I'm sitting in the garden."], ["Mark", "Lucky you! Oh, my bus is coming. Bye!"]],
      qs: [
        { q: "Где Марк?", a: ["На остановке", "Дома", "В саду"], c: 0 },
        { q: "Какая погода у Марка?", a: ["Идёт снег", "Солнечно", "Дождь"], c: 0 },
        { q: "Что делает Лиз?", a: ["Сидит в саду", "Ждёт автобус", "Работает"], c: 0 },
        { q: "Что надето на Марке?", a: ["Большое пальто и шапка", "Лёгкая куртка", "Футболка"], c: 0 }
      ]
    },
    speak: ["What are you doing?", "I'm waiting for the bus.", "It's raining now.", "What's the weather like?"],
    write: {
      trans: [["Сейчас идёт дождь.", ["It is raining now", "It's raining now", "It is raining", "It's raining"]], ["Что ты делаешь?", ["What are you doing"]], ["На ней красное платье.", ["She is wearing a red dress", "She's wearing a red dress"]], ["Мы не смотрим телевизор.", ["We aren't watching TV", "We are not watching TV", "We're not watching TV", "We don't watch TV"]]],
      prompt: "Опиши, что происходит прямо сейчас: какая погода за окном, что на тебе надето, что делают люди рядом.",
      minWords: 35, use: ["is", "wearing", "weather", "now"],
      model: "Now I am sitting at home. The weather is cold and cloudy. It is raining. I am wearing jeans and a warm blue shirt. My wife is reading a book and my son is playing a game."
    }
  },
  {
    t: "Где ты был",
    words: [
      ["was", "был (I, he, she, it)", "уоз"], ["were", "были (we, you, they)", "уёр"], ["yesterday", "вчера", "йЕстэдэй"], ["last", "прошлый", "ласт"], ["ago", "назад", "эгОу"],
      ["born", "рождённый (I was born — я родился)", "борн"], ["party", "вечеринка", "пАрти"], ["concert", "концерт", "кОнсэт"], ["holiday", "отпуск, праздник", "хОлидэй"], ["beach", "пляж", "бич"],
      ["sea", "море", "си"], ["mountain", "гора", "мАунтин"], ["village", "деревня", "вИлидж"], ["abroad", "за границей", "эбрОд"], ["trip", "поездка", "трип"],
      ["tired", "уставший", "тАйэд"], ["busy", "занятой", "бИзи"], ["ill", "больной", "ил"], ["angry", "сердитый", "Энгри"], ["hungry", "голодный", "хАнгри"],
      ["great", "отличный", "грэйт"], ["bad", "плохой", "бэд"], ["terrible", "ужасный", "тЭрибл"], ["amazing", "потрясающий", "эмЭйзинг"], ["crowded", "многолюдный", "крАудид"],
      ["quiet", "тихий", "кУайэт"], ["noisy", "шумный", "нОйзи"], ["first", "первый", "фёрст"], ["last night", "вчера вечером", "ласт найт"], ["then", "тогда, потом", "зэн"]
    ],
    phrases: [["Where were you yesterday?", "Где ты был вчера?"], ["I was at home.", "Я был дома."], ["It was amazing!", "Было потрясающе!"], ["Were you tired?", "Ты устал?"], ["We were at the beach last week.", "На прошлой неделе мы были на пляже."], ["I was born in Moscow.", "Я родился в Москве."]],
    grammar: {
      title: "was / were: был, была, были",
      text: "Прошедшее время от to be: I, he, she, it — was; we, you, they — were. Отрицание: wasn't, weren't. Вопрос — was / were в начало: Were you at home? — Yes, I was. / No, I wasn't. Слова прошлого: yesterday, last night, last week, two days ago (два дня назад). «Я родился» по-английски — I was born.",
      examples: [["I was at a concert last night.", "Вчера вечером я был на концерте."], ["They were in Spain two years ago.", "Два года назад они были в Испании."], ["She wasn't at work yesterday.", "Вчера её не было на работе."], ["Were you tired?", "Ты устал?"]],
      quiz: [
        { q: "I ___ at home yesterday.", a: ["was", "were", "am"], c: 0 }, { q: "We ___ at the beach last week.", a: ["were", "was", "are"], c: 0 },
        { q: "___ you at the party?", a: ["Were", "Was", "Did"], c: 0 }, { q: "She ___ at work yesterday. (не)", a: ["wasn't", "weren't", "didn't"], c: 0 },
        { q: "It ___ a great concert.", a: ["was", "were", "is was"], c: 0 }, { q: "They ___ tired after the trip.", a: ["were", "was", "did"], c: 0 },
        { q: "Where ___ he last night?", a: ["was", "were", "did"], c: 0 }, { q: "I was born ___ Moscow.", a: ["in", "at", "on"], c: 0 }
      ]
    },
    read: {
      title: "Лето в Сочи",
      text: "Last summer I was on holiday in Sochi with my friends. The weather was hot and sunny. Our hotel was near the sea, and the beach was always crowded. One day we were in the mountains: it was quiet and beautiful, and the air was clean. In the evenings we were very tired but happy. The food was great, but the hotel was a bit noisy at night. It was an amazing trip!",
      gloss: [["summer", "лето"], ["one day", "однажды"], ["air", "воздух"], ["a bit", "немного"]],
      qs: [
        { q: "Где был автор прошлым летом?", a: ["В Сочи", "В Москве", "За границей"], c: 0 },
        { q: "Какой был пляж?", a: ["Всегда многолюдный", "Тихий", "Грязный"], c: 0 },
        { q: "Как было в горах?", a: ["Тихо и красиво", "Шумно", "Холодно"], c: 0 },
        { q: "Что было не так с отелем?", a: ["Ночью было шумно", "Плохая еда", "Далеко от моря"], c: 0 }
      ]
    },
    listen: {
      lines: [["Sue", "Hi, Mike! Where were you last week? You weren't at work."], ["Mike", "I was ill. I was at home for five days."], ["Sue", "Oh no! Are you OK now?"], ["Mike", "Yes, thanks. And where were you on Saturday?"], ["Sue", "I was at a concert with my sister. It was amazing!"], ["Mike", "Was it crowded?"], ["Sue", "Yes, there were about two thousand people!"]],
      qs: [
        { q: "Почему Майка не было на работе?", a: ["Он болел", "Был в отпуске", "Был на концерте"], c: 0 },
        { q: "Сколько дней он был дома?", a: ["5", "2", "7"], c: 0 },
        { q: "Где была Сью в субботу?", a: ["На концерте с сестрой", "На работе", "Дома"], c: 0 },
        { q: "Сколько там было людей?", a: ["Около 2000", "Около 200", "Около 20 000"], c: 0 }
      ]
    },
    speak: ["Where were you yesterday?", "I was at home.", "It was amazing!", "We were at the beach last week."],
    write: {
      trans: [["Вчера я был дома.", ["I was at home yesterday", "Yesterday I was at home"]], ["В прошлом году мы были на море.", ["We were at the sea last year", "Last year we were at the sea", "We were at the seaside last year", "Last year we were at the seaside", "We were by the sea last year"]], ["Ты устал?", ["Were you tired", "Are you tired"]], ["Концерт был потрясающим.", ["The concert was amazing"]]],
      prompt: "Расскажи, где ты был в прошлые выходные или в последнем отпуске: где, с кем, какая была погода, как было.",
      minWords: 40, use: ["was", "were", "last", "it was"],
      model: "Last weekend I was in a village with my family. The weather was warm and sunny. My parents were happy. It was quiet and the air was clean. On Sunday evening we were very tired. It was a great weekend."
    }
  },
  {
    t: "Выходные и отпуск",
    words: [
      ["went", "ходил, ездил (go)", "уэнт"], ["saw", "видел (see)", "со"], ["had", "имел, ел (have)", "хэд"], ["did", "делал (do)", "дид"], ["came", "пришёл, приехал (come)", "кэйм"],
      ["bought", "купил (buy)", "бот"], ["ate", "ел (eat)", "эйт"], ["drank", "пил (drink)", "дрэнк"], ["took", "взял (take)", "тук"], ["made", "сделал (make)", "мэйд"],
      ["got", "получил, добрался (get)", "гот"], ["met", "встретил (meet)", "мэт"], ["gave", "дал (give)", "гэйв"], ["found", "нашёл (find)", "фАунд"], ["lost", "потерял (lose)", "лост"],
      ["wrote", "написал (write)", "роут"], ["spoke", "говорил (speak)", "спОук"], ["slept", "спал (sleep)", "слэпт"], ["swam", "плавал (swim)", "суэм"], ["flew", "летел (fly)", "флу"],
      ["visited", "посетил", "вИзитид"], ["watched", "смотрел", "уотчт"], ["played", "играл", "плэйд"], ["walked", "гулял", "уокт"], ["stayed", "остановился, жил (в отеле)", "стэйд"],
      ["cooked", "приготовил", "кукт"], ["tried", "попробовал", "трайд"], ["enjoyed", "наслаждался", "инджОйд"], ["started", "начал", "стАртид"], ["finished", "закончил", "фИништ"]
    ],
    phrases: [["What did you do at the weekend?", "Что ты делал в выходные?"], ["I visited my parents.", "Я навестил родителей."], ["Did you have a good time?", "Хорошо провёл время?"], ["We went to the seaside.", "Мы ездили на море."], ["I didn't see the film.", "Я не видел этот фильм."], ["How was your holiday?", "Как прошёл отпуск?"]],
    grammar: {
      title: "Past Simple: что сделал в прошлом",
      text: "Правильные глаголы получают -ed: visit → visited, play → played, stay → stayed. Неправильные надо запомнить: go → went, see → saw, eat → ate, buy → bought. Форма одна для всех: I went, she went. Отрицание — didn't + глагол в начальной форме: I didn't go (не didn't went!). Вопрос — Did: Did you see the sea? — Yes, I did. / No, I didn't.",
      examples: [["We visited a museum.", "Мы сходили в музей."], ["I went to the cinema yesterday.", "Вчера я ходил в кино."], ["She didn't buy the dress.", "Она не купила платье."], ["Did you see the sea?", "Ты видел море?"]],
      quiz: [
        { q: "Yesterday I ___ to the cinema.", a: ["went", "go", "goed"], c: 0 }, { q: "We ___ a museum last week.", a: ["visited", "visit", "visiting"], c: 0 },
        { q: "___ you see the film?", a: ["Did", "Do", "Were"], c: 0 }, { q: "I didn't ___ any bread.", a: ["buy", "bought", "buys"], c: 0 },
        { q: "She ___ a cake for my birthday.", a: ["made", "maked", "make"], c: 0 }, { q: "They ___ in a nice hotel.", a: ["stayed", "staied", "stay"], c: 0 },
        { q: "Did you have a good time? — Yes, I ___.", a: ["did", "was", "had"], c: 0 }, { q: "He ___ the sea for the first time.", a: ["saw", "seed", "see"], c: 0 }
      ]
    },
    read: {
      title: "Выходные у моря",
      text: "Last weekend Ben and Lisa went to the seaside. They took the train on Saturday morning and got there at eleven. First they found their hotel and left their bags. Then they walked on the beach and swam in the sea. For lunch they ate fresh fish in a small restaurant. In the afternoon Lisa bought some presents, and Ben played volleyball with some new friends. In the evening they watched the sunset. They didn't want to go home on Sunday!",
      gloss: [["seaside", "морское побережье"], ["left their bags", "оставили сумки"], ["lunch", "обед"], ["volleyball", "волейбол"], ["sunset", "закат"]],
      qs: [
        { q: "Как они добрались до моря?", a: ["На поезде", "На машине", "На самолёте"], c: 0 },
        { q: "Что они ели на обед?", a: ["Свежую рыбу", "Пиццу", "Курицу"], c: 0 },
        { q: "Что делал Бен днём?", a: ["Играл в волейбол", "Покупал подарки", "Спал"], c: 0 },
        { q: "Что они делали вечером?", a: ["Смотрели на закат", "Ходили в кино", "Готовили ужин"], c: 0 }
      ]
    },
    listen: {
      lines: [["Jack", "How was your holiday, Emma?"], ["Emma", "It was great! We went to Italy."], ["Jack", "Lucky you! What did you do there?"], ["Emma", "We visited Rome and saw a lot of old buildings. And we ate a lot of pizza!"], ["Jack", "Did you go to the sea?"], ["Emma", "No, we didn't. There wasn't time."], ["Jack", "How long did you stay?"], ["Emma", "Ten days."]],
      qs: [
        { q: "Куда ездила Эмма?", a: ["В Италию", "В Испанию", "Во Францию"], c: 0 },
        { q: "Какой город они посетили?", a: ["Рим", "Милан", "Венецию"], c: 0 },
        { q: "Они ездили на море?", a: ["Нет, не хватило времени", "Да", "Не сказано"], c: 0 },
        { q: "Сколько дней они там были?", a: ["10", "7", "14"], c: 0 }
      ]
    },
    speak: ["What did you do at the weekend?", "I visited my parents.", "Did you have a good time?", "We went to the seaside."],
    write: {
      trans: [["Вчера мы ходили в кино.", ["We went to the cinema yesterday", "Yesterday we went to the cinema", "We went to the movies yesterday"]], ["Я не видел этот фильм.", ["I didn't see this film", "I didn't see the film", "I didn't see that film", "I haven't seen this film"]], ["Ты купил хлеб?", ["Did you buy bread", "Did you buy the bread", "Did you buy any bread", "Did you buy some bread"]], ["Она приготовила ужин.", ["She made dinner", "She cooked dinner", "She made the dinner", "She cooked the dinner"]]],
      prompt: "Расскажи о прошлых выходных или отпуске: что ты делал, куда ходил, что видел и что ел.",
      minWords: 45, use: ["went", "saw", "ate", "visited"],
      model: "Last weekend I went to Kazan with my wife. We took the train on Saturday. We visited the old town and saw the Kremlin. For lunch we ate soup and fish. In the evening we walked by the river. On Sunday we bought some presents and came home."
    }
  }
];
M.exam = {
  read: {
    title: "Дарья",
    text: "My name is Daria. I'm twenty-six and I live in Novosibirsk. I'm a manager in a big company. Every day I get up at seven, have breakfast and take the metro to work. I don't like my job very much, but my colleagues are nice. Last month I was on holiday in Turkey with my husband. We stayed in a hotel near the beach. The weather was hot and sunny every day. We swam in the sea, visited an old town and ate a lot of good food. Now I'm sitting at my desk and looking at our photos. I want to go back!",
    gloss: [["desk", "рабочий стол"], ["photos", "фотографии"], ["go back", "вернуться"]],
    qs: [
      { q: "Кем работает Дарья?", a: ["Менеджером", "Учителем", "Врачом"], c: 0 }, { q: "Как она добирается на работу?", a: ["На метро", "На автобусе", "Пешком"], c: 0 },
      { q: "Где она была в прошлом месяце?", a: ["В Турции", "В Италии", "В Сочи"], c: 0 }, { q: "Какая там была погода?", a: ["Жарко и солнечно каждый день", "Дождливо", "Холодно"], c: 0 },
      { q: "Что она делает сейчас?", a: ["Сидит за столом и смотрит фото", "Плавает в море", "Собирает чемодан"], c: 0 }
    ]
  },
  listen: {
    lines: [["Tourist", "Excuse me, is this the way to the museum?"], ["Woman", "No, it isn't. Go back to the square, then turn left."], ["Tourist", "Is it far?"], ["Woman", "Not very. About ten minutes on foot. It's opposite the big hotel."], ["Tourist", "Thank you. Is it open today?"], ["Woman", "Yes, but it closes at five."], ["Tourist", "Oh, it's four o'clock now!"], ["Woman", "Then take a taxi!"]],
    qs: [
      { q: "Турист идёт к музею правильно?", a: ["Нет, не туда", "Да", "Не сказано"], c: 0 }, { q: "Куда повернуть на площади?", a: ["Налево", "Направо", "Идти прямо"], c: 0 },
      { q: "Где музей?", a: ["Напротив большого отеля", "Рядом с вокзалом", "На площади"], c: 0 }, { q: "Во сколько закрывается музей?", a: ["В 5", "В 4", "В 10"], c: 0 },
      { q: "Что советуют туристу?", a: ["Взять такси", "Идти пешком", "Прийти завтра"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Вчера я был на работе.", ["I was at work yesterday", "Yesterday I was at work"]],
      ["Она сейчас готовит ужин.", ["She is cooking dinner now", "She's cooking dinner now", "She is making dinner now", "She's making dinner now", "She is cooking dinner", "She's cooking dinner"]],
      ["В прошлом году мы ездили на море.", ["We went to the sea last year", "Last year we went to the sea", "We went to the seaside last year", "Last year we went to the seaside"]],
      ["Где аптека?", ["Where is the pharmacy", "Where's the pharmacy"]],
      ["Он не умеет водить машину.", ["He can't drive", "He cannot drive", "He can't drive a car", "He cannot drive a car"]]
    ],
    prompt: "Напиши письмо другу: кто ты и чем занимаешься, как проходит обычный день, что ты делаешь сейчас и где был в последнем отпуске.",
    minWords: 60, use: ["usually", "now", "was", "went"],
    model: "Hi Sam! I'm Misha, I'm twenty-two and I'm a programmer. I usually get up at seven and work from home. I often go to the gym after work. Now I'm sitting in a café and drinking coffee. It's raining outside. Last summer I went to Sochi with my girlfriend. The weather was hot and the sea was warm. It was amazing!"
  },
  speak: ["Excuse me, how can I get to the station?", "I usually get up at seven.", "It's raining and it's cold.", "Last summer we went to the sea.", "I was at home yesterday."],
  grammar: [
    { q: "She ___ TV now.", a: ["is watching", "watches", "watching"], c: 0 }, { q: "Where ___ you yesterday?", a: ["were", "was", "did"], c: 0 },
    { q: "We ___ to Italy last year.", a: ["went", "go", "goed"], c: 0 }, { q: "___ you visit the museum?", a: ["Did", "Were", "Do"], c: 0 },
    { q: "He usually ___ to work by bus.", a: ["goes", "is going", "go"], c: 0 }, { q: "___ left at the bank.", a: ["Turn", "Turning", "To turn"], c: 0 }
  ]
};
})();

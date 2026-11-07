// Месяц 2 (A1): Повседневная жизнь.
(function(){
const M = window.MD_PROGRAM.en.months[1];
M.weeks = [
  {
    t: "Мой день",
    words: [
      ["get up", "вставать", "гет ап"], ["wake up", "просыпаться", "уэйк ап"], ["wash", "мыть(ся)", "уош"], ["have breakfast", "завтракать", "хэв брЭкфаст"], ["go", "идти, ехать", "гоу"],
      ["work", "работать", "уёрк"], ["study", "учиться", "стАди"], ["come home", "приходить домой", "кам хоум"], ["cook", "готовить (еду)", "кук"], ["sleep", "спать", "слип"],
      ["eat", "есть (кушать)", "ит"], ["drink", "пить", "дринк"], ["read", "читать", "рид"], ["watch TV", "смотреть телевизор", "уотч ти-вИ"], ["listen to", "слушать", "лисн ту"],
      ["play", "играть", "плэй"], ["walk", "гулять, ходить пешком", "уок"], ["live", "жить", "лив"], ["like", "нравиться, любить", "лайк"], ["want", "хотеть", "уонт"],
      ["every day", "каждый день", "Эври дэй"], ["usually", "обычно", "Южуэли"], ["at work", "на работе", "эт уёрк"], ["at home", "дома", "эт хоум"], ["before", "до, перед", "бифО"],
      ["after", "после", "Афтэр"], ["early", "рано", "Ёрли"], ["late", "поздно", "лэйт"], ["week", "неделя", "уик"], ["weekend", "выходные", "уикЭнд"]
    ],
    phrases: [["I get up at seven.", "Я встаю в семь."], ["What do you do every day?", "Что ты делаешь каждый день?"], ["I go to work by bus.", "Я езжу на работу на автобусе."], ["We have breakfast at eight.", "Мы завтракаем в восемь."], ["Do you like coffee?", "Ты любишь кофе?"], ["I don't work at the weekend.", "Я не работаю в выходные."]],
    grammar: {
      title: "Present Simple: то, что мы делаем обычно",
      text: "Present Simple — время для привычек и того, что происходит регулярно: каждый день, обычно, по выходным. Для I, you, we, they глагол берём как в словаре: I work, we live. Отрицание — don't + глагол: I don't work. Вопрос — Do в начало: Do you work? Короткие ответы: Yes, I do. / No, I don't.",
      examples: [["I work every day.", "Я работаю каждый день."], ["We don't cook in the morning.", "Мы не готовим по утрам."], ["Do you live in Moscow?", "Ты живёшь в Москве?"], ["They usually walk after work.", "Они обычно гуляют после работы."]],
      quiz: [
        { q: "I ___ at seven.", a: ["get up", "gets up", "getting up"], c: 0 }, { q: "We ___ TV in the evening.", a: ["watch", "watches", "are watch"], c: 0 },
        { q: "___ you like tea?", a: ["Do", "Are", "Does"], c: 0 }, { q: "I ___ like coffee.", a: ["don't", "doesn't", "not"], c: 0 },
        { q: "They ___ in London.", a: ["live", "lives", "are live"], c: 0 }, { q: "Do you work? — Yes, I ___.", a: ["do", "am", "work"], c: 0 },
        { q: "We ___ breakfast at eight.", a: ["have", "has", "are have"], c: 0 }, { q: "You ___ to work by bus.", a: ["go", "goes", "going"], c: 0 }
      ]
    },
    read: {
      title: "День Дэна",
      text: "Hi, I'm Dan. I live in Kazan with my wife. Every day I get up at half past six. I have breakfast and go to work by bus. I work in an office from nine to five. After work I usually walk in the park. In the evening we cook dinner together and watch TV. I go to bed at eleven. At the weekend I don't work: I sleep late and play football with my friends.",
      gloss: [["half past six", "половина седьмого"], ["office", "офис"], ["dinner", "ужин"], ["together", "вместе"], ["go to bed", "ложиться спать"], ["football", "футбол"]],
      qs: [
        { q: "Во сколько Дэн встаёт?", a: ["В 6:30", "В 7:30", "В 6:00"], c: 0 },
        { q: "Как он добирается на работу?", a: ["На автобусе", "Пешком", "На машине"], c: 0 },
        { q: "Что он обычно делает после работы?", a: ["Гуляет в парке", "Играет в футбол", "Готовит ужин один"], c: 0 },
        { q: "Что он делает в выходные?", a: ["Спит дольше и играет в футбол", "Работает", "Весь день смотрит телевизор"], c: 0 }
      ]
    },
    listen: {
      lines: [["Kate", "Do you get up early, Nick?"], ["Nick", "Yes, I do. I get up at six."], ["Kate", "Wow! Why?"], ["Nick", "I work in a hospital. I start at seven."], ["Kate", "Do you have breakfast?"], ["Nick", "No, I don't. I only drink coffee."], ["Kate", "And what do you do after work?"], ["Nick", "I come home, cook dinner and read."]],
      qs: [
        { q: "Во сколько Ник встаёт?", a: ["В 6", "В 7", "В 8"], c: 0 },
        { q: "Где он работает?", a: ["В больнице", "В школе", "В офисе"], c: 0 },
        { q: "Ник завтракает?", a: ["Нет, только пьёт кофе", "Да, кашей", "Не сказано"], c: 0 },
        { q: "Что он делает после работы?", a: ["Готовит ужин и читает", "Гуляет", "Смотрит телевизор"], c: 0 }
      ]
    },
    speak: ["I get up at seven.", "I go to work by bus.", "Do you like coffee?", "I don't work at the weekend."],
    write: {
      trans: [["Я встаю в семь.", ["I get up at seven", "I get up at seven o'clock", "I wake up at seven", "I wake up at seven o'clock"]], ["Мы не готовим утром.", ["We don't cook in the morning"]], ["Ты живёшь в Москве?", ["Do you live in Moscow"]], ["Они обычно гуляют после работы.", ["They usually walk after work", "They usually go for a walk after work"]]],
      prompt: "Опиши свой обычный день: когда встаёшь, что делаешь утром, днём и вечером, что делаешь в выходные.",
      minWords: 35, use: ["get up", "usually", "after", "every day"],
      model: "Every day I get up at seven. I have breakfast and go to work by metro. I work from nine to six. After work I usually walk in the park. In the evening I cook dinner and read. At the weekend I sleep late."
    }
  },
  {
    t: "Работа и люди",
    words: [
      ["doctor", "врач", "дОктэр"], ["nurse", "медсестра", "нёрс"], ["driver", "водитель", "дрАйвэр"], ["engineer", "инженер", "инджинИэр"], ["manager", "менеджер", "мЭнэджэр"],
      ["programmer", "программист", "прОуграмэр"], ["shop assistant", "продавец", "шоп эсИстэнт"], ["chef", "повар", "шэф"], ["waiter", "официант", "уЭйтэр"], ["builder", "строитель", "бИлдэр"],
      ["job", "работа (должность)", "джоб"], ["office", "офис", "Офис"], ["hospital", "больница", "хОспитл"], ["school", "школа", "скул"], ["shop", "магазин", "шоп"],
      ["company", "компания", "кАмпэни"], ["money", "деньги", "мАни"], ["colleague", "коллега", "кОлиг"], ["boss", "начальник", "бос"], ["customer", "клиент, покупатель", "кАстэмэр"],
      ["start", "начинать", "старт"], ["finish", "заканчивать", "фИниш"], ["help", "помогать", "хэлп"], ["drive", "водить (машину)", "драйв"], ["make", "делать, изготавливать", "мэйк"],
      ["sell", "продавать", "сэл"], ["earn", "зарабатывать", "ёрн"], ["teach", "учить, преподавать", "тич"], ["speak", "говорить", "спик"], ["know", "знать", "ноу"]
    ],
    phrases: [["What do you do?", "Кем ты работаешь?"], ["I'm a programmer.", "Я программист."], ["Where does she work?", "Где она работает?"], ["She works in a hospital.", "Она работает в больнице."], ["He doesn't like his job.", "Ему не нравится его работа."], ["Does your boss speak English?", "Твой начальник говорит по-английски?"]],
    grammar: {
      title: "Present Simple: he, she, it — окончание -s, does и doesn't",
      text: "Когда говорим про одного человека (he, she, it), к глаголу добавляем -s: she works, he lives. После o, s, sh, ch, x — -es: goes, watches. Согласная + y → ies: study → studies. Have → has. Отрицание — doesn't + глагол без -s: He doesn't drive. Вопрос — Does: Does she work here? — Yes, she does. / No, she doesn't.",
      examples: [["She works in a hospital.", "Она работает в больнице."], ["He doesn't drive.", "Он не водит машину."], ["Does your sister speak English?", "Твоя сестра говорит по-английски?"], ["My father teaches at school.", "Мой отец преподаёт в школе."]],
      quiz: [
        { q: "She ___ in an office.", a: ["works", "work", "working"], c: 0 }, { q: "He ___ to work by car.", a: ["goes", "go", "gos"], c: 0 },
        { q: "My mother ___ TV every evening.", a: ["watches", "watchs", "watch"], c: 0 }, { q: "___ he speak English?", a: ["Does", "Do", "Is"], c: 0 },
        { q: "She ___ like coffee.", a: ["doesn't", "don't", "isn't"], c: 0 }, { q: "Tom ___ two children.", a: ["has", "have", "haves"], c: 0 },
        { q: "Does she work here? — No, she ___.", a: ["doesn't", "don't", "isn't"], c: 0 }, { q: "He ___ Russian at school.", a: ["studies", "studys", "study"], c: 0 }
      ]
    },
    read: {
      title: "Мария и Алекс",
      text: "My sister Maria is a nurse. She works in a big hospital in the city centre. She starts work at seven in the morning and finishes at three. She helps doctors and talks to patients. Maria likes her job, but it is very hard. Her husband, Alex, is a programmer. He works at home, so he doesn't drive to work. He earns good money, but he works a lot. They have one son, Leo. He is five.",
      gloss: [["centre", "центр"], ["talk to", "разговаривать с"], ["patients", "пациенты"], ["hard", "тяжёлый, трудный"], ["so", "поэтому"], ["a lot", "много"]],
      qs: [
        { q: "Кем работает Мария?", a: ["Медсестрой", "Врачом", "Программистом"], c: 0 },
        { q: "Во сколько она заканчивает работу?", a: ["В 3", "В 7", "В 5"], c: 0 },
        { q: "Где работает Алекс?", a: ["Дома", "В больнице", "В офисе"], c: 0 },
        { q: "Сколько лет их сыну?", a: ["5", "3", "7"], c: 0 }
      ]
    },
    listen: {
      lines: [["Anna", "What does your brother do?"], ["Ben", "He's a driver. He drives a bus in the city."], ["Anna", "Does he like it?"], ["Ben", "Yes, he does. But he starts very early, at five."], ["Anna", "And your sister?"], ["Ben", "She's a teacher. She teaches English at a school."], ["Anna", "Does she speak French too?"], ["Ben", "No, she doesn't."]],
      qs: [
        { q: "Кем работает брат Бена?", a: ["Водителем автобуса", "Учителем", "Поваром"], c: 0 },
        { q: "Во сколько он начинает работу?", a: ["В 5", "В 7", "В 9"], c: 0 },
        { q: "Что преподаёт сестра?", a: ["Английский", "Французский", "Математику"], c: 0 },
        { q: "Сестра говорит по-французски?", a: ["Нет", "Да", "Немного"], c: 0 }
      ]
    },
    speak: ["What do you do?", "I'm a programmer.", "She works in a hospital.", "Does your boss speak English?"],
    write: {
      trans: [["Она работает в больнице.", ["She works in a hospital", "She works at a hospital", "She works in the hospital", "She works at the hospital"]], ["Он не водит машину.", ["He doesn't drive", "He doesn't drive a car"]], ["Твой брат говорит по-английски?", ["Does your brother speak English"]], ["Мой отец инженер.", ["My father is an engineer", "My dad is an engineer", "My father works as an engineer"]]],
      prompt: "Расскажи, кем работают ты и твои близкие: где, когда начинают и заканчивают, нравится ли им работа.",
      minWords: 35, use: ["works", "doesn't", "job", "starts"],
      model: "My mother is a doctor. She works in a hospital. She starts at eight and finishes at four. She likes her job. My father is a driver. He doesn't like his job because he starts very early."
    }
  },
  {
    t: "Еда и магазин",
    words: [
      ["bread", "хлеб", "брэд"], ["milk", "молоко", "милк"], ["cheese", "сыр", "чиз"], ["meat", "мясо", "мит"], ["fish", "рыба", "фиш"],
      ["egg", "яйцо", "эг"], ["apple", "яблоко", "Эпл"], ["potato", "картофель", "пэтЭйтоу"], ["rice", "рис", "райс"], ["vegetables", "овощи", "вЭджтэблз"],
      ["water", "вода", "уОтэр"], ["tea", "чай", "ти"], ["coffee", "кофе", "кОфи"], ["juice", "сок", "джус"], ["sugar", "сахар", "шУгэр"],
      ["salt", "соль", "солт"], ["chicken", "курица", "чИкин"], ["soup", "суп", "суп"], ["cake", "торт, пирожное", "кэйк"], ["fruit", "фрукты", "фрут"],
      ["some", "немного, несколько", "сам"], ["any", "какой-нибудь (в вопросах и с not)", "Эни"], ["much", "много (не считается)", "мач"], ["many", "много (считается)", "мЭни"], ["how much", "сколько, сколько стоит", "хАу мач"],
      ["price", "цена", "прайс"], ["buy", "покупать", "бай"], ["pay", "платить", "пэй"], ["cheap", "дешёвый", "чип"], ["expensive", "дорогой", "икспЭнсив"]
    ],
    phrases: [["How much is it?", "Сколько это стоит?"], ["I'd like a coffee, please.", "Я бы хотел кофе, пожалуйста."], ["Can I have the bill, please?", "Можно счёт, пожалуйста?"], ["Is there any milk?", "Молоко есть?"], ["We need some bread.", "Нам нужен хлеб."], ["That's too expensive.", "Это слишком дорого."]],
    grammar: {
      title: "some и any, much и many, вежливое I'd like",
      text: "Одни слова можно посчитать (an apple, two eggs), другие нельзя (water, milk, bread, money). Some — «немного, несколько» — в утверждениях: There is some milk. Any — в вопросах и отрицаниях: Are there any eggs? We don't have any bread. Сколько: How many — для того, что считается (How many apples?), How much — для того, что не считается (How much water?) и для цены (How much is it?). Вежливо попросить: I'd like… = I would like… — «Я бы хотел…».",
      examples: [["There is some milk in the fridge.", "В холодильнике есть молоко."], ["Are there any eggs?", "Есть яйца?"], ["We don't have any bread.", "У нас нет хлеба."], ["How many apples do you want?", "Сколько яблок ты хочешь?"]],
      quiz: [
        { q: "There is ___ cheese on the table.", a: ["some", "any", "many"], c: 0 }, { q: "Are there ___ eggs?", a: ["any", "some", "much"], c: 0 },
        { q: "We don't have ___ sugar.", a: ["any", "some", "many"], c: 0 }, { q: "How ___ apples do you need?", a: ["many", "much", "any"], c: 0 },
        { q: "How ___ water do you drink?", a: ["much", "many", "any"], c: 0 }, { q: "___ like a tea, please.", a: ["I'd", "I'm", "I"], c: 0 },
        { q: "How much ___ this cake?", a: ["is", "are", "does"], c: 0 }, { q: "I need two ___. (яйцо)", a: ["eggs", "egg", "egges"], c: 0 }
      ]
    },
    read: {
      title: "Суббота Ольги",
      text: "Every Saturday Olga goes to the market. The food there is fresh and not expensive. She buys potatoes, vegetables, apples and some chicken. She doesn't buy any meat because her family doesn't eat it. Then she goes to a café and has a coffee and a piece of cake. She usually pays about two thousand roubles for everything.",
      gloss: [["market", "рынок"], ["fresh", "свежий"], ["because", "потому что"], ["a piece of", "кусочек"], ["about", "примерно"], ["thousand", "тысяча"], ["everything", "всё"]],
      qs: [
        { q: "Когда Ольга ходит на рынок?", a: ["По субботам", "Каждый день", "По воскресеньям"], c: 0 },
        { q: "Почему она не покупает мясо?", a: ["Её семья его не ест", "Оно дорогое", "Его нет на рынке"], c: 0 },
        { q: "Что она делает после рынка?", a: ["Пьёт кофе с пирожным в кафе", "Идёт домой", "Готовит обед"], c: 0 },
        { q: "Сколько она обычно платит?", a: ["Около 2000 рублей", "Около 200 рублей", "Около 20 000 рублей"], c: 0 }
      ]
    },
    listen: {
      lines: [["Seller", "Good morning! Can I help you?"], ["Woman", "Yes, I'd like some apples, please."], ["Seller", "How many?"], ["Woman", "Six, please. And how much is the cheese?"], ["Seller", "It's five pounds."], ["Woman", "OK, and some bread."], ["Seller", "Here you are. Anything else?"], ["Woman", "No, thank you. How much is it?"], ["Seller", "That's nine pounds fifty."]],
      qs: [
        { q: "Сколько яблок покупает женщина?", a: ["6", "5", "9"], c: 0 },
        { q: "Сколько стоит сыр?", a: ["5 фунтов", "9 фунтов", "50 пенсов"], c: 0 },
        { q: "Что ещё она берёт?", a: ["Хлеб", "Молоко", "Рыбу"], c: 0 },
        { q: "Сколько всего?", a: ["9 фунтов 50 пенсов", "5 фунтов 90 пенсов", "6 фунтов 50 пенсов"], c: 0 }
      ]
    },
    speak: ["How much is it?", "I'd like a coffee, please.", "Is there any milk?", "We need some bread."],
    write: {
      trans: [["Я бы хотел чай, пожалуйста.", ["I'd like a tea please", "I would like a tea please", "I'd like tea please", "I would like tea please", "I'd like a cup of tea please", "I would like a cup of tea please"]], ["Есть ли яйца?", ["Are there any eggs", "Do we have any eggs", "Do you have any eggs", "Have you got any eggs"]], ["Сколько это стоит?", ["How much is it", "How much is this", "How much does it cost", "How much does this cost"]], ["У нас нет хлеба.", ["We don't have any bread", "We have no bread", "We haven't got any bread", "We don't have bread"]]],
      prompt: "Напиши, что ты обычно ешь и пьёшь за день и что покупаешь в магазине.",
      minWords: 35, use: ["some", "any", "buy", "drink"],
      model: "In the morning I drink coffee and eat some bread with cheese. For lunch I usually have soup and chicken. I don't drink any juice. On Saturday I buy some vegetables, fruit and fish in the supermarket."
    }
  },
  {
    t: "Свободное время",
    words: [
      ["hobby", "хобби", "хОби"], ["free time", "свободное время", "фри тайм"], ["music", "музыка", "мьЮзик"], ["film", "фильм", "филм"], ["game", "игра", "гэйм"],
      ["sport", "спорт", "спорт"], ["football", "футбол", "фУтбол"], ["swim", "плавать", "суим"], ["dance", "танцевать", "дэнс"], ["sing", "петь", "синг"],
      ["draw", "рисовать", "дро"], ["run", "бегать", "ран"], ["ride a bike", "кататься на велосипеде", "райд э байк"], ["travel", "путешествовать", "трЭвэл"], ["meet", "встречать(ся)", "мит"],
      ["visit", "навещать, посещать", "вИзит"], ["park", "парк", "парк"], ["cinema", "кинотеатр", "сИнэма"], ["gym", "спортзал", "джим"], ["guitar", "гитара", "гитАр"],
      ["can", "мочь, уметь", "кэн"], ["always", "всегда", "Олуэйз"], ["often", "часто", "Офн"], ["sometimes", "иногда", "сАмтаймз"], ["never", "никогда", "нЭвэр"],
      ["love", "очень любить", "лав"], ["hate", "ненавидеть", "хэйт"], ["interesting", "интересный", "Интрэстинг"], ["boring", "скучный", "бОринг"], ["fun", "весело, веселье", "фан"]
    ],
    phrases: [["What do you do in your free time?", "Чем ты занимаешься в свободное время?"], ["I can swim, but I can't dance.", "Я умею плавать, но не умею танцевать."], ["I love reading.", "Я очень люблю читать."], ["How often do you go to the gym?", "Как часто ты ходишь в спортзал?"], ["Let's go to the cinema!", "Пойдём в кино!"], ["That sounds fun!", "Звучит весело!"]],
    grammar: {
      title: "can / can't, like + -ing и слова «как часто»",
      text: "Can — «могу, умею». После него глагол без to и без -s, для всех одинаково: I can swim, she can swim. Отрицание — can't, вопрос — Can you drive? После like, love, hate глагол обычно с -ing: I love dancing, she hates running. Слова always, usually, often, sometimes, never ставим перед глаголом (We often go to the cinema), но после am / is / are (He is never late).",
      examples: [["I can play the guitar.", "Я умею играть на гитаре."], ["She can't swim.", "Она не умеет плавать."], ["I love dancing.", "Я очень люблю танцевать."], ["We often go to the cinema.", "Мы часто ходим в кино."], ["He is never late.", "Он никогда не опаздывает."]],
      quiz: [
        { q: "I ___ swim very well.", a: ["can", "cans", "can to"], c: 0 }, { q: "___ you play the guitar?", a: ["Can", "Do can", "Are"], c: 0 },
        { q: "She can ___ English.", a: ["speak", "speaks", "to speak"], c: 0 }, { q: "I love ___.", a: ["dancing", "dance", "dances"], c: 0 },
        { q: "We ___ go to the gym on Mondays. (часто)", a: ["often", "oftenly", "are often"], c: 0 }, { q: "He is ___ late. (никогда)", a: ["never", "not never", "nevers"], c: 0 },
        { q: "I ___ play football. (иногда)", a: ["sometimes", "some time", "sometime ago"], c: 0 }, { q: "They don't like ___ TV.", a: ["watching", "watch", "watches"], c: 0 }
      ]
    },
    read: {
      title: "Свободное время Кейт",
      text: "Hi! I'm Kate. In my free time I love sport. I can swim and I often go to the gym after work. On Sundays I ride a bike in the park with my husband. I can't sing, but I love music: I sometimes play the guitar. My husband never goes to the gym — he hates running! He likes films, so we often go to the cinema on Friday evening. It's always fun.",
      gloss: [["on Sundays", "по воскресеньям"], ["with", "с"], ["Friday", "пятница"], ["so", "поэтому"]],
      qs: [
        { q: "Куда Кейт часто ходит после работы?", a: ["В спортзал", "В кино", "В парк"], c: 0 },
        { q: "Что она делает по воскресеньям?", a: ["Катается на велосипеде в парке", "Плавает", "Поёт"], c: 0 },
        { q: "Что ненавидит её муж?", a: ["Бег", "Кино", "Музыку"], c: 0 },
        { q: "Когда они ходят в кино?", a: ["В пятницу вечером", "В воскресенье", "Каждый день"], c: 0 }
      ]
    },
    listen: {
      lines: [["Lily", "What do you do in your free time, Sam?"], ["Sam", "I play football with my friends."], ["Lily", "How often?"], ["Sam", "Twice a week. And you?"], ["Lily", "I love dancing. I go to dance classes on Tuesday."], ["Sam", "Can you teach me?"], ["Lily", "Ha! Sure. Can you sing?"], ["Sam", "No, I can't. I'm a terrible singer!"]],
      qs: [
        { q: "Чем Сэм занимается в свободное время?", a: ["Играет в футбол", "Танцует", "Поёт"], c: 0 },
        { q: "Как часто?", a: ["Два раза в неделю", "Каждый день", "Раз в месяц"], c: 0 },
        { q: "Когда у Лили танцы?", a: ["Во вторник", "В пятницу", "В субботу"], c: 0 },
        { q: "Сэм умеет петь?", a: ["Нет", "Да", "Немного"], c: 0 }
      ]
    },
    speak: ["What do you do in your free time?", "I can swim, but I can't dance.", "I love reading.", "Let's go to the cinema!"],
    write: {
      trans: [["Я умею плавать.", ["I can swim"]], ["Она не умеет петь.", ["She can't sing", "She cannot sing"]], ["Мы часто ходим в кино.", ["We often go to the cinema", "We often go to the movies"]], ["Я люблю танцевать.", ["I love dancing", "I like dancing", "I love to dance", "I like to dance"]]],
      prompt: "Расскажи о своём свободном времени: что ты умеешь и не умеешь, что любишь делать и как часто.",
      minWords: 40, use: ["can", "often", "love", "free time"],
      model: "In my free time I love sport. I can swim and run, but I can't dance. I often go to the gym after work. I sometimes play the guitar. At the weekend we usually go to the cinema. I never watch TV."
    }
  }
];
M.exam = {
  read: {
    title: "Пол — повар",
    text: "Paul is thirty-two. He is a chef in a small Italian restaurant. He works from Tuesday to Saturday. He starts at eleven in the morning and finishes late, at about midnight. He doesn't have much free time, but on Sundays and Mondays he relaxes. He often goes swimming, and he sometimes visits his parents in the country. Paul can cook very well, of course, but at home he never cooks — he usually eats in a café! He likes his job because it's interesting, but he doesn't earn much money.",
    gloss: [["Italian", "итальянский"], ["restaurant", "ресторан"], ["midnight", "полночь"], ["relax", "отдыхать"], ["in the country", "за городом"], ["of course", "конечно"]],
    qs: [
      { q: "Кем работает Пол?", a: ["Поваром", "Официантом", "Водителем"], c: 0 }, { q: "Какие у него выходные?", a: ["Воскресенье и понедельник", "Суббота и воскресенье", "Только вторник"], c: 0 },
      { q: "Когда он заканчивает работу?", a: ["Около полуночи", "В 11 утра", "В 6 вечера"], c: 0 }, { q: "Готовит ли он дома?", a: ["Никогда", "Всегда", "Иногда"], c: 0 },
      { q: "Почему ему нравится работа?", a: ["Она интересная", "Там много платят", "Там мало работы"], c: 0 }
    ]
  },
  listen: {
    lines: [["Tom", "Hi, Jane! Are you free on Saturday?"], ["Jane", "In the morning I'm not. I always go to the gym. But in the afternoon I'm free."], ["Tom", "Great! Let's go to the market and buy some food for the party."], ["Jane", "Good idea. How many people are there?"], ["Tom", "About ten. We need some cheese, bread and fruit."], ["Jane", "And drinks?"], ["Tom", "Yes, some juice and water. Can you buy a cake?"], ["Jane", "Sure!"]],
    qs: [
      { q: "Когда Джейн свободна в субботу?", a: ["Днём", "Утром", "Вечером"], c: 0 }, { q: "Что она делает утром?", a: ["Ходит в спортзал", "Работает", "Спит"], c: 0 },
      { q: "Сколько человек будет на вечеринке?", a: ["Около 10", "5", "20"], c: 0 }, { q: "Что должна купить Джейн?", a: ["Торт", "Сыр", "Сок"], c: 0 },
      { q: "Зачем они идут на рынок?", a: ["Купить еду для вечеринки", "Погулять", "Работать"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Мой брат работает в больнице.", ["My brother works in a hospital", "My brother works at a hospital", "My brother works in the hospital", "My brother works at the hospital"]],
      ["Она не пьёт кофе.", ["She doesn't drink coffee"]],
      ["Ты умеешь водить машину?", ["Can you drive", "Can you drive a car"]],
      ["Сколько стоит этот торт?", ["How much is this cake", "How much does this cake cost"]],
      ["Я обычно встаю в семь.", ["I usually get up at seven", "I usually wake up at seven", "I usually get up at seven o'clock", "I usually wake up at seven o'clock"]]
    ],
    prompt: "Напиши письмо другу о своей неделе: работа или учёба, еда, свободное время, что ты умеешь делать.",
    minWords: 50, use: ["usually", "can", "some", "work"],
    model: "Hi Tom! I usually get up at seven and go to work by bus. I work in an office. My boss is nice. For lunch I eat some soup and drink tea. After work I often go to the gym. I can swim, but I can't dance. At the weekend I visit my parents."
  },
  speak: ["I usually get up at seven.", "She works in a hospital.", "How much is the cheese?", "I can swim, but I can't sing.", "We often go to the cinema."],
  grammar: [
    { q: "He ___ in an office.", a: ["works", "work", "is work"], c: 0 }, { q: "___ your sister like tea?", a: ["Does", "Do", "Is"], c: 0 },
    { q: "I don't have ___ money.", a: ["any", "some", "many"], c: 0 }, { q: "How ___ eggs do we need?", a: ["many", "much", "any"], c: 0 },
    { q: "She can ___ the guitar.", a: ["play", "plays", "to play"], c: 0 }, { q: "They ___ go to the gym. (никогда)", a: ["never", "not never", "don't never"], c: 0 }
  ]
};
})();

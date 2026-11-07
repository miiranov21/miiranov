// Месяц 1 (A1): Знакомство и основы. Слова: [английский, русский, транскрипция русскими буквами, ударная гласная заглавная].
(function(){
const M = window.MD_PROGRAM.en.months[0];
M.weeks = [
  {
    t: "Знакомство",
    words: [
      ["hello", "привет", "хэлОу"], ["hi", "привет (просто)", "хай"], ["goodbye", "до свидания", "гудбАй"], ["please", "пожалуйста", "плиз"], ["thank you", "спасибо", "сэнк ю"],
      ["yes", "да", "йес"], ["no", "нет", "ноу"], ["sorry", "извините", "сОри"], ["name", "имя", "нэйм"], ["friend", "друг", "фрэнд"],
      ["I", "я", "ай"], ["you", "ты, вы", "ю"], ["he", "он", "хи"], ["she", "она", "ши"], ["it", "оно, это", "ит"],
      ["we", "мы", "уи"], ["they", "они", "зэй"], ["am", "есть (с I)", "эм"], ["is", "есть (с he, she, it)", "из"], ["are", "есть (с we, you, they)", "а"],
      ["country", "страна", "кАнтри"], ["city", "город", "сИти"], ["from", "из", "фром"], ["Russia", "Россия", "рАша"], ["England", "Англия", "Инглэнд"],
      ["English", "английский", "Инглиш"], ["Russian", "русский", "рАшн"], ["student", "студент", "стьЮдэнт"], ["teacher", "учитель", "тИчэр"], ["good", "хороший", "гуд"]
    ],
    phrases: [["Nice to meet you.", "Приятно познакомиться."], ["How are you?", "Как дела?"], ["I'm fine, thanks.", "Хорошо, спасибо."], ["What's your name?", "Как тебя зовут?"], ["My name is Anna.", "Меня зовут Анна."], ["Where are you from?", "Откуда ты?"]],
    grammar: {
      title: "Глагол to be: am, is, are",
      text: "В английском в предложении всегда нужен глагол. Там, где по-русски мы говорим «Я студент», по-английски говорят «Я есть студент»: I am a student. Форма зависит от того, кто: I am; he, she, it is; we, you, they are. Отрицание: добавь not (I am not, she is not). Вопрос: поставь am / is / are в начало (Are you a student?). В речи сокращают: I'm, he's, she's, we're, they're, isn't, aren't.",
      examples: [["I am a student.", "Я студент."], ["She is from Russia.", "Она из России."], ["We are friends.", "Мы друзья."], ["Are you a teacher?", "Ты учитель?"]],
      quiz: [
        { q: "I ___ Anna.", a: ["am", "is", "are"], c: 0 }, { q: "She ___ a teacher.", a: ["is", "am", "are"], c: 0 },
        { q: "We ___ from Russia.", a: ["are", "is", "am"], c: 0 }, { q: "___ you a student?", a: ["Are", "Is", "Am"], c: 0 },
        { q: "He ___ my friend.", a: ["is", "are", "am"], c: 0 }, { q: "They ___ from England.", a: ["are", "is", "am"], c: 0 },
        { q: "I ___ not a teacher.", a: ["am", "is", "are"], c: 0 }, { q: "It ___ a good city.", a: ["is", "are", "am"], c: 0 }
      ]
    },
    read: {
      title: "Анна и Том",
      text: "Hello! My name is Anna. I am from Russia. I am a student. My friend is Tom. He is from England. He is a teacher. Tom is very nice. We are good friends.",
      gloss: [["very", "очень"], ["nice", "приятный, милый"]],
      qs: [
        { q: "Откуда Анна?", a: ["Из России", "Из Англии", "Не сказано"], c: 0 },
        { q: "Кто Том по профессии?", a: ["Учитель", "Студент", "Врач"], c: 0 },
        { q: "Откуда Том?", a: ["Из Англии", "Из России", "Из Америки"], c: 0 },
        { q: "Кто Анна и Том друг другу?", a: ["Друзья", "Брат и сестра", "Коллеги"], c: 0 }
      ]
    },
    listen: {
      lines: [["Max", "Hi! I'm Max. What's your name?"], ["Lena", "Hello, Max. My name is Lena."], ["Max", "Nice to meet you, Lena. Where are you from?"], ["Lena", "I'm from Moscow. And you?"], ["Max", "I'm from London."], ["Lena", "Are you a student?"], ["Max", "No, I'm not. I'm a teacher."]],
      qs: [
        { q: "Как зовут девушку?", a: ["Лена", "Анна", "Мария"], c: 0 },
        { q: "Откуда Лена?", a: ["Из Москвы", "Из Лондона", "Из Казани"], c: 0 },
        { q: "Откуда Макс?", a: ["Из Лондона", "Из Москвы", "Из Нью-Йорка"], c: 0 },
        { q: "Макс студент?", a: ["Нет, он учитель", "Да, студент", "Не сказано"], c: 0 }
      ]
    },
    speak: ["Nice to meet you.", "I am from Russia.", "How are you?", "We are good friends."],
    write: {
      trans: [["Я студент.", ["I am a student", "I'm a student"]], ["Она из России.", ["She is from Russia", "She's from Russia"]], ["Мы друзья.", ["We are friends", "We're friends"]], ["Ты учитель?", ["Are you a teacher"]]],
      prompt: "Представься: как тебя зовут, откуда ты, кто ты (студент, учитель…), кто твой друг и откуда он.",
      minWords: 20, use: ["name", "from", "am", "friend"],
      model: "Hello! My name is Misha. I am from Russia. I am a student. My friend is Anna. She is from Moscow. She is a teacher."
    }
  },
  {
    t: "Семья",
    words: [
      ["family", "семья", "фЭмили"], ["mother", "мама", "мАзэр"], ["father", "папа", "фАзэр"], ["brother", "брат", "брАзэр"], ["sister", "сестра", "сИстэр"],
      ["son", "сын", "сан"], ["daughter", "дочь", "дОтэр"], ["husband", "муж", "хАзбэнд"], ["wife", "жена", "уайф"], ["child", "ребёнок", "чайлд"],
      ["my", "мой", "май"], ["your", "твой, ваш", "ёр"], ["his", "его", "хиз"], ["her", "её", "хёр"], ["our", "наш", "Ауэр"],
      ["their", "их", "зэар"], ["this", "этот, это", "зис"], ["that", "тот, то", "зэт"], ["parents", "родители", "пЭрэнтс"], ["children", "дети", "чИлдрэн"],
      ["old", "старый", "оулд"], ["young", "молодой", "янг"], ["tall", "высокий", "тол"], ["short", "низкий, короткий", "шорт"], ["big", "большой", "биг"],
      ["small", "маленький", "смол"], ["happy", "счастливый", "хЭпи"], ["nice", "милый, приятный", "найс"], ["man", "мужчина", "мэн"], ["woman", "женщина", "вУмэн"]
    ],
    phrases: [["This is my mother.", "Это моя мама."], ["Who is this?", "Кто это?"], ["Is he your brother?", "Он твой брат?"], ["Her name is Kate.", "Её зовут Кейт."], ["They are my parents.", "Это мои родители."], ["We are a big family.", "У нас большая семья."]],
    grammar: {
      title: "Чей? my, your, his, her, our, their и this / that",
      text: "Слова «мой, твой, его…» ставятся перед существительным и не меняются: my mother, my father, my parents. I → my, you → your, he → his, she → her, we → our, they → their. This — «это, этот» про то, что рядом; that — «то, тот» про то, что дальше. This is my brother — Это мой брат.",
      examples: [["This is my brother.", "Это мой брат."], ["That is her husband.", "Это её муж (вон тот)."], ["Our parents are young.", "Наши родители молодые."], ["Is this your son?", "Это твой сын?"]],
      quiz: [
        { q: "This is ___ sister. (моя)", a: ["my", "me", "I"], c: 0 }, { q: "Kate is ___ wife. (его)", a: ["his", "he", "her"], c: 0 },
        { q: "___ name is Tom. (Его)", a: ["His", "He", "Him"], c: 0 }, { q: "Is this ___ phone? (твой)", a: ["your", "you", "yours"], c: 0 },
        { q: "___ parents are old. (Наши)", a: ["Our", "We", "Us"], c: 0 }, { q: "They love ___ children. (их)", a: ["their", "they", "them"], c: 0 },
        { q: "Anna and ___ husband are happy. (её)", a: ["her", "she", "his"], c: 0 }, { q: "___ is my father. (Это, рядом)", a: ["This", "Those", "They"], c: 0 }
      ]
    },
    read: {
      title: "Моя семья",
      text: "This is my family. My father is Ivan. He is tall and very kind. My mother is Olga. She is a teacher. My brother is Pavel. He is young: he is ten. My sister Kate is a student. Our family is big and happy.",
      gloss: [["kind", "добрый"], ["very", "очень"], ["ten", "десять"]],
      qs: [
        { q: "Кем работает мама?", a: ["Учитель", "Врач", "Студентка"], c: 0 },
        { q: "Какой папа?", a: ["Высокий и добрый", "Низкий", "Молодой и весёлый"], c: 0 },
        { q: "Сколько лет брату?", a: ["10", "12", "20"], c: 0 },
        { q: "Какая это семья?", a: ["Большая и счастливая", "Маленькая", "Не сказано"], c: 0 }
      ]
    },
    listen: {
      lines: [["Tom", "Who is this?"], ["Anna", "This is my sister, Mary."], ["Tom", "She is very young!"], ["Anna", "Yes, she is a student."], ["Tom", "And who is that man?"], ["Anna", "That is her husband, John. He is a doctor."], ["Tom", "They are a nice family."]],
      qs: [
        { q: "Кто такая Мэри?", a: ["Сестра Анны", "Мама Анны", "Дочь Анны"], c: 0 },
        { q: "Мэри…", a: ["студентка", "врач", "учитель"], c: 0 },
        { q: "Кто такой Джон?", a: ["Муж Мэри", "Брат Анны", "Отец Анны"], c: 0 },
        { q: "Кем работает Джон?", a: ["Врачом", "Учителем", "Он студент"], c: 0 }
      ]
    },
    speak: ["This is my family.", "My mother is young.", "Who is that man?", "Our parents are happy."],
    write: {
      trans: [["Это мой брат.", ["This is my brother"]], ["Её муж высокий.", ["Her husband is tall"]], ["Наши родители молодые.", ["Our parents are young"]], ["Это твоя дочь?", ["Is this your daughter", "Is that your daughter"]]],
      prompt: "Расскажи о своей семье: кто это, как зовут, какой человек (высокий, молодой, добрый…).",
      minWords: 25, use: ["my", "is", "are", "family"],
      model: "This is my family. My mother is Olga. She is young and nice. My father is Ivan. He is tall. My sister is a student. We are a happy family."
    }
  },
  {
    t: "Числа, возраст и время",
    words: [
      ["one", "один", "уан"], ["two", "два", "ту"], ["three", "три", "сри"], ["four", "четыре", "фор"], ["five", "пять", "файв"],
      ["six", "шесть", "сикс"], ["seven", "семь", "сЭвэн"], ["eight", "восемь", "эйт"], ["nine", "девять", "найн"], ["ten", "десять", "тэн"],
      ["eleven", "одиннадцать", "илЭвэн"], ["twelve", "двенадцать", "твэлв"], ["twenty", "двадцать", "твЭнти"], ["thirty", "тридцать", "сЁрти"], ["forty", "сорок", "фОрти"],
      ["fifty", "пятьдесят", "фИфти"], ["hundred", "сто", "хАндрэд"], ["age", "возраст", "эйдж"], ["year", "год", "йиэр"], ["number", "число, номер", "нАмбэр"],
      ["time", "время", "тайм"], ["hour", "час", "Ауэр"], ["minute", "минута", "мИнит"], ["o'clock", "ровно (о часах)", "эклОк"], ["morning", "утро", "мОрнинг"],
      ["afternoon", "день (после полудня)", "афтэрнУн"], ["evening", "вечер", "Ивнинг"], ["night", "ночь", "найт"], ["today", "сегодня", "тудЭй"], ["now", "сейчас", "нАу"]
    ],
    phrases: [["How old are you?", "Сколько тебе лет?"], ["I am twenty years old.", "Мне двадцать лет."], ["What time is it?", "Который час?"], ["It's seven o'clock.", "Сейчас семь часов."], ["What's your phone number?", "Какой у тебя номер телефона?"], ["See you in the evening.", "Увидимся вечером."]],
    grammar: {
      title: "Множественное число и вопросы с How old / What time",
      text: "Чтобы сказать «много», к слову добавляют -s: friend → friends, minute → minutes. После s, sh, ch, x добавляют -es: class → classes. Если слово кончается на согласную + y, y меняется на ies: city → cities. Есть особые слова: man → men, woman → women, child → children. Возраст говорят через to be: I am twenty (years old) — «Я есть двадцать». Вопросы: How old are you? What time is it?",
      examples: [["one city — two cities", "один город — два города"], ["a man — three men", "мужчина — трое мужчин"], ["How old are your children?", "Сколько лет твоим детям?"], ["It is five o'clock.", "Сейчас пять часов."]],
      quiz: [
        { q: "five ___ (друг)", a: ["friends", "friend", "friendes"], c: 0 }, { q: "three ___ (город)", a: ["cities", "citys", "city"], c: 0 },
        { q: "two ___ (мужчина)", a: ["men", "mans", "man"], c: 0 }, { q: "four ___ (ребёнок)", a: ["children", "childs", "child"], c: 0 },
        { q: "How old ___ you?", a: ["are", "is", "am"], c: 0 }, { q: "How old ___ your brother?", a: ["is", "are", "am"], c: 0 },
        { q: "ten ___ (минута)", a: ["minutes", "minute", "minuts"], c: 0 }, { q: "two ___ (женщина)", a: ["women", "womans", "woman"], c: 0 }
      ]
    },
    read: {
      title: "День Сэма",
      text: "My name is Sam. I am twenty-five years old. I am a student. Today is a busy day. In the morning, at eight o'clock, I am at university. In the afternoon, at two o'clock, I am at work. In the evening, at seven o'clock, I am at home with my family.",
      gloss: [["busy", "занятой, загруженный"], ["at university", "в университете"], ["at work", "на работе"], ["at home", "дома"], ["with", "с"]],
      qs: [
        { q: "Сколько лет Сэму?", a: ["25", "20", "15"], c: 0 },
        { q: "Где Сэм в 8 утра?", a: ["В университете", "На работе", "Дома"], c: 0 },
        { q: "Где он в 2 часа дня?", a: ["На работе", "Дома", "В университете"], c: 0 },
        { q: "Когда он дома с семьёй?", a: ["В 7 вечера", "В 8 утра", "В 2 часа дня"], c: 0 }
      ]
    },
    listen: {
      lines: [["Ben", "Hi, Kate! How old is your daughter now?"], ["Kate", "She is six. And my son is twelve."], ["Ben", "Wow! What time is it?"], ["Kate", "It's five o'clock."], ["Ben", "Oh, I'm late! What's your phone number?"], ["Kate", "It's four, five, nine, two, seven."], ["Ben", "Thanks! See you in the evening."]],
      qs: [
        { q: "Сколько лет дочери Кейт?", a: ["6", "12", "16"], c: 0 },
        { q: "Сколько лет её сыну?", a: ["12", "6", "20"], c: 0 },
        { q: "Который час?", a: ["5:00", "4:00", "7:00"], c: 0 },
        { q: "Номер телефона Кейт:", a: ["45927", "54927", "45972"], c: 0 }
      ]
    },
    speak: ["What time is it?", "It's seven o'clock.", "I am twenty years old.", "See you in the evening."],
    write: {
      trans: [["Сколько тебе лет?", ["How old are you"]], ["Мне двадцать лет.", ["I am twenty", "I am twenty years old", "I'm twenty", "I'm twenty years old"]], ["Который час?", ["What time is it", "What is the time", "What's the time"]], ["Сейчас три часа.", ["It is three o'clock", "It's three o'clock", "It is three o'clock now", "It's three o'clock now", "It is three", "It's three"]]],
      prompt: "Напиши о себе и о семье с числами: сколько тебе лет, сколько лет родным, где ты утром и вечером (например: In the morning I am at work).",
      minWords: 25, use: ["years", "old", "morning", "evening"],
      model: "I am twenty-two years old. My sister is nineteen. My father is fifty. In the morning, at nine o'clock, I am at work. In the evening I am at home."
    }
  },
  {
    t: "Мой дом",
    words: [
      ["house", "дом", "хаус"], ["flat", "квартира", "флэт"], ["room", "комната", "рум"], ["kitchen", "кухня", "кИтчин"], ["bedroom", "спальня", "бЭдрум"],
      ["bathroom", "ванная", "бАсрум"], ["window", "окно", "уИндоу"], ["door", "дверь", "до"], ["table", "стол", "тэйбл"], ["chair", "стул", "чэа"],
      ["bed", "кровать", "бэд"], ["sofa", "диван", "сОуфа"], ["lamp", "лампа", "лэмп"], ["book", "книга", "бук"], ["phone", "телефон", "фоун"],
      ["picture", "картина", "пИкчэр"], ["cup", "чашка", "кап"], ["key", "ключ", "ки"], ["bag", "сумка", "бэг"], ["wall", "стена", "уол"],
      ["in", "в", "ин"], ["on", "на", "он"], ["under", "под", "Андэр"], ["next to", "рядом с", "нэкст ту"], ["behind", "за, позади", "бихАйнд"],
      ["there is", "есть, находится (один)", "зэар из"], ["there are", "есть, находятся (много)", "зэар а"], ["new", "новый", "нью"], ["clean", "чистый", "клин"], ["beautiful", "красивый", "бьЮтифул"]
    ],
    phrases: [["Welcome to my flat!", "Добро пожаловать ко мне!"], ["Where is my phone?", "Где мой телефон?"], ["It's on the table.", "Он на столе."], ["There are two bedrooms.", "Здесь две спальни."], ["Is there a sofa?", "Там есть диван?"], ["My room is small but nice.", "Моя комната маленькая, но уютная."]],
    grammar: {
      title: "there is / there are и артикли a, an, the",
      text: "Когда говорим, что где-то что-то есть, начинаем с there is (один предмет) или there are (много): There is a sofa in the room — В комнате есть диван. Вопрос: Is there…? Are there…? Артикль a ставят перед одним предметом, когда говорим о нём впервые: a lamp. Если слово начинается с гласного звука — an: an old house. The — когда понятно, о каком предмете речь: The key is on the table — Ключ (тот самый) на столе.",
      examples: [["There is a sofa in the room.", "В комнате есть диван."], ["There are two windows.", "Там два окна."], ["Is there a lamp?", "Там есть лампа?"], ["The key is on the table.", "Ключ на столе."]],
      quiz: [
        { q: "There ___ a bed in the room.", a: ["is", "are", "am"], c: 0 }, { q: "There ___ three chairs.", a: ["are", "is", "am"], c: 0 },
        { q: "___ there a kitchen?", a: ["Is", "Are", "Am"], c: 0 }, { q: "It is ___ old house.", a: ["an", "a", "two"], c: 0 },
        { q: "It is ___ big flat.", a: ["a", "an", "are"], c: 0 }, { q: "The book is ___ the table. (на)", a: ["on", "in", "under"], c: 0 },
        { q: "The cat is ___ the bed. (под)", a: ["under", "on", "in"], c: 0 }, { q: "The keys are ___ my bag. (в)", a: ["in", "on", "under"], c: 0 }
      ]
    },
    read: {
      title: "Моя квартира",
      text: "This is my flat. It is small but beautiful. There are three rooms: a kitchen, a bedroom and a living room. In the bedroom there is a big bed and a lamp. In the living room there is a sofa and a table. There are two pictures on the wall. My cat is always under the sofa!",
      gloss: [["living room", "гостиная"], ["cat", "кот, кошка"], ["always", "всегда"], ["but", "но"]],
      qs: [
        { q: "Сколько комнат в квартире?", a: ["Три", "Две", "Четыре"], c: 0 },
        { q: "Что стоит в спальне?", a: ["Большая кровать и лампа", "Диван и стол", "Картины"], c: 0 },
        { q: "Где картины?", a: ["На стене", "На столе", "Под диваном"], c: 0 },
        { q: "Где обычно кот?", a: ["Под диваном", "На кровати", "На кухне"], c: 0 }
      ]
    },
    listen: {
      lines: [["Son", "Mum, where is my phone?"], ["Mum", "Is it on the table in the kitchen?"], ["Son", "No, it isn't."], ["Mum", "Is it in your bag?"], ["Son", "No…"], ["Mum", "Look! It's on the sofa, next to the lamp."], ["Son", "Oh, thank you! And where are my keys?"], ["Mum", "They're in the door!"]],
      qs: [
        { q: "Что сын ищет сначала?", a: ["Телефон", "Ключи", "Сумку"], c: 0 },
        { q: "Где телефон?", a: ["На диване рядом с лампой", "На кухне", "В сумке"], c: 0 },
        { q: "Где ключи?", a: ["В двери", "На столе", "Под диваном"], c: 0 },
        { q: "Телефон был в сумке?", a: ["Нет", "Да", "Не сказано"], c: 0 }
      ]
    },
    speak: ["Where is my phone?", "It's on the table.", "There are two bedrooms.", "My room is small but nice."],
    write: {
      trans: [["В комнате есть кровать.", ["There is a bed in the room"]], ["Ключи на столе.", ["The keys are on the table"]], ["Там есть кухня?", ["Is there a kitchen", "Is there a kitchen there"]], ["Моя квартира новая и чистая.", ["My flat is new and clean", "My apartment is new and clean"]]],
      prompt: "Опиши свою квартиру или комнату: что в ней есть и где стоит. Используй there is / there are и in, on, next to.",
      minWords: 30, use: ["there is", "there are", "in", "on"],
      model: "My flat is new and clean. There are two rooms and a kitchen. In my room there is a bed, a table and a chair. There is a lamp on the table. There are three pictures on the wall."
    }
  }
];
M.exam = {
  read: {
    title: "Письмо от Люси",
    text: "Hi! I'm Lucy. I am nineteen years old and I am from Manchester, a big city in England. I am a student. This is my family: my mother is a teacher, my father is a doctor and my brother Jack is twelve. Our house is not big, but it is nice. There are three bedrooms and a small kitchen. My room is next to the bathroom. There is a bed, a table and a lot of books in my room.",
    gloss: [["a lot of", "много"], ["doctor", "врач"]],
    qs: [
      { q: "Сколько лет Люси?", a: ["19", "12", "16"], c: 0 }, { q: "Откуда она?", a: ["Из Манчестера", "Из Лондона", "Из Москвы"], c: 0 },
      { q: "Кем работает её мама?", a: ["Учителем", "Врачом", "Она студентка"], c: 0 }, { q: "Сколько спален в доме?", a: ["Три", "Две", "Одна"], c: 0 },
      { q: "Что рядом с её комнатой?", a: ["Ванная", "Кухня", "Комната брата"], c: 0 }
    ]
  },
  listen: {
    lines: [["Guest", "Good morning! Is this the Green Hotel?"], ["Woman", "Yes, it is. What's your name, please?"], ["Guest", "My name is Peter Black."], ["Woman", "Nice to meet you, Mr Black. Your room is number fifteen."], ["Guest", "Thank you. Is there a phone in the room?"], ["Woman", "Yes, there is. And there are two beds."], ["Guest", "Great. What time is breakfast?"], ["Woman", "At eight o'clock."]],
    qs: [
      { q: "Как зовут гостя?", a: ["Питер Блэк", "Питер Грин", "Пол Блэк"], c: 0 }, { q: "Номер его комнаты?", a: ["15", "50", "5"], c: 0 },
      { q: "Что есть в номере?", a: ["Телефон и две кровати", "Телефон и диван", "Одна кровать"], c: 0 }, { q: "Во сколько завтрак?", a: ["В 8:00", "В 9:00", "В 7:00"], c: 0 },
      { q: "Когда идёт разговор?", a: ["Утром", "Вечером", "Ночью"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Меня зовут Анна, я из России.", ["My name is Anna I am from Russia", "My name is Anna I'm from Russia", "My name is Anna and I am from Russia", "My name is Anna and I'm from Russia", "My name's Anna I'm from Russia", "I am Anna I am from Russia", "I'm Anna I'm from Russia"]],
      ["Это мой отец, он учитель.", ["This is my father he is a teacher", "This is my father he's a teacher", "This is my dad he is a teacher", "This is my dad he's a teacher"]],
      ["В квартире три комнаты.", ["There are three rooms in the flat", "There are three rooms in the apartment", "There are three rooms in my flat", "There are three rooms in my apartment"]],
      ["Сколько лет твоей сестре?", ["How old is your sister"]],
      ["Телефон под кроватью.", ["The phone is under the bed", "My phone is under the bed"]]
    ],
    prompt: "Напиши письмо новому другу: представься, расскажи о семье и о своём доме.",
    minWords: 40, use: ["my", "is", "are", "there"],
    model: "Hi! My name is Misha. I am twenty-two years old and I am from Russia. My mother is a teacher and my father is a doctor. My sister is nineteen. Our flat is big and clean. There are three rooms and a kitchen. My room is next to the kitchen."
  },
  speak: ["Hello, my name is Anna.", "I am from Russia.", "This is my brother.", "There are two rooms in my flat.", "What time is it?"],
  grammar: [
    { q: "My sister ___ a student.", a: ["is", "are", "am"], c: 0 }, { q: "___ there two windows?", a: ["Are", "Is", "Am"], c: 0 },
    { q: "His ___ are young. (дети)", a: ["children", "childs", "child"], c: 0 }, { q: "This is ___ flat. (наша)", a: ["our", "we", "us"], c: 0 },
    { q: "Where ___ my keys?", a: ["are", "is", "am"], c: 0 }, { q: "It is ___ apple.", a: ["an", "a", "two"], c: 0 }
  ]
};
})();

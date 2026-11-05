// Курс английского для русскоговорящих: с нуля до базового уровня (A1 → A2).
// Каждая тема: 10 слов, 4 фразы, короткое правило и 3 вопроса по грамматике.
// Слова: [английский, русский]. Фразы: [английский, русский].
// quiz: q — предложение с пропуском, a — варианты, c — номер правильного варианта.
window.MD_COURSE = {
  id: "en",
  name: "Английский",
  voice: "en-US",
  units: [
    {
      id: "u1", icon: "👋", title: "Приветствия",
      words: [["hello", "привет"], ["goodbye", "до свидания"], ["please", "пожалуйста"], ["thank you", "спасибо"], ["yes", "да"],
              ["no", "нет"], ["sorry", "извините"], ["good morning", "доброе утро"], ["good night", "спокойной ночи"], ["friend", "друг"]],
      phrases: [["Hello, how are you?", "Привет, как дела?"], ["I am fine, thank you.", "У меня всё хорошо, спасибо."],
                ["Nice to meet you.", "Приятно познакомиться."], ["See you later.", "Увидимся позже."]],
      grammar: {
        title: "Глагол to be: am, is, are",
        text: "В английском нельзя сказать просто «Я Анна». Нужен глагол «быть»: I am, you are, he / she / it is, we / they are.",
        examples: [["I am Anna.", "Я Анна."], ["You are my friend.", "Ты мой друг."], ["He is happy.", "Он счастлив."]]
      },
      quiz: [
        { q: "I ___ Mike.", a: ["am", "is", "are"], c: 0 },
        { q: "She ___ my friend.", a: ["are", "is", "am"], c: 1 },
        { q: "We ___ fine, thank you.", a: ["is", "am", "are"], c: 2 }
      ]
    },
    {
      id: "u2", icon: "👨‍👩‍👧", title: "Я и семья",
      words: [["mother", "мама"], ["father", "папа"], ["sister", "сестра"], ["brother", "брат"], ["family", "семья"],
              ["name", "имя"], ["man", "мужчина"], ["woman", "женщина"], ["child", "ребёнок"], ["husband", "муж"]],
      phrases: [["My name is Anna.", "Меня зовут Анна."], ["This is my brother.", "Это мой брат."],
                ["She is my sister.", "Она моя сестра."], ["I love my family.", "Я люблю свою семью."]],
      grammar: {
        title: "Мой, твой, его, её: my, your, his, her",
        text: "Притяжательные слова стоят перед существительным: my — мой, your — твой / ваш, his — его, her — её, our — наш, their — их.",
        examples: [["my mother", "моя мама"], ["his name", "его имя"], ["our family", "наша семья"]]
      },
      quiz: [
        { q: "This is Tom. ___ sister is Kate.", a: ["Her", "His", "My"], c: 1 },
        { q: "This is Anna. ___ brother is Max.", a: ["Her", "His", "Our"], c: 0 },
        { q: "We love ___ family.", a: ["their", "your", "our"], c: 2 }
      ]
    },
    {
      id: "u3", icon: "🔢", title: "Числа и время",
      words: [["one", "один"], ["two", "два"], ["three", "три"], ["five", "пять"], ["ten", "десять"],
              ["today", "сегодня"], ["tomorrow", "завтра"], ["morning", "утро"], ["evening", "вечер"], ["hour", "час"]],
      phrases: [["I have two sisters.", "У меня две сестры."], ["See you tomorrow.", "Увидимся завтра."],
                ["What time is it?", "Который час?"], ["It is five o'clock.", "Сейчас пять часов."]],
      grammar: {
        title: "Множественное число: -s",
        text: "Чтобы сказать «много», к слову обычно добавляют -s: book → books. После s, sh, ch, x добавляют -es: box → boxes. Есть исключения: child → children, man → men.",
        examples: [["two books", "две книги"], ["three boxes", "три коробки"], ["five children", "пять детей"]]
      },
      quiz: [
        { q: "I have three ___.", a: ["book", "books", "bookes"], c: 1 },
        { q: "Two ___ are in the park.", a: ["mans", "man", "men"], c: 2 },
        { q: "She has two ___.", a: ["boxes", "boxs", "box"], c: 0 }
      ]
    },
    {
      id: "u4", icon: "🍎", title: "Еда",
      words: [["water", "вода"], ["bread", "хлеб"], ["apple", "яблоко"], ["coffee", "кофе"], ["tea", "чай"],
              ["milk", "молоко"], ["egg", "яйцо"], ["cheese", "сыр"], ["breakfast", "завтрак"], ["dinner", "ужин"]],
      phrases: [["I would like a coffee, please.", "Мне кофе, пожалуйста."], ["I eat an apple every day.", "Я ем яблоко каждый день."],
                ["The water is cold.", "Вода холодная."], ["What is for dinner?", "Что на ужин?"]],
      grammar: {
        title: "Артикли a и an",
        text: "Перед одним предметом, о котором говорят впервые, ставят a. Если слово начинается с гласного звука, ставят an: an apple, an egg.",
        examples: [["a cup of tea", "чашка чая"], ["an apple", "яблоко"], ["an egg", "яйцо"]]
      },
      quiz: [
        { q: "I want ___ egg.", a: ["a", "an", "—"], c: 1 },
        { q: "She has ___ sandwich.", a: ["an", "a", "—"], c: 1 },
        { q: "He eats ___ orange.", a: ["an", "a", "—"], c: 0 }
      ]
    },
    {
      id: "u5", icon: "🏠", title: "Дом",
      words: [["house", "дом"], ["room", "комната"], ["kitchen", "кухня"], ["bed", "кровать"], ["table", "стол"],
              ["door", "дверь"], ["window", "окно"], ["chair", "стул"], ["big", "большой"], ["small", "маленький"]],
      phrases: [["The kitchen is big.", "Кухня большая."], ["My room is small.", "Моя комната маленькая."],
                ["There is a table in the room.", "В комнате есть стол."], ["Open the window, please.", "Открой окно, пожалуйста."]],
      grammar: {
        title: "There is / there are",
        text: "Так говорят, что где-то что-то есть. There is — для одного предмета, there are — для нескольких. Место обычно ставят в конце.",
        examples: [["There is a bed in my room.", "В моей комнате есть кровать."], ["There are two chairs.", "Там два стула."], ["There is a cat in the kitchen.", "На кухне кошка."]]
      },
      quiz: [
        { q: "There ___ a window in the kitchen.", a: ["are", "is", "am"], c: 1 },
        { q: "There ___ three rooms in the house.", a: ["is", "are", "be"], c: 1 },
        { q: "There ___ a big table.", a: ["is", "are", "have"], c: 0 }
      ]
    },
    {
      id: "u6", icon: "🏃", title: "Действия",
      words: [["go", "идти"], ["eat", "есть"], ["drink", "пить"], ["read", "читать"], ["sleep", "спать"],
              ["work", "работать"], ["study", "учиться"], ["run", "бегать"], ["like", "нравиться"], ["want", "хотеть"]],
      phrases: [["I like to read books.", "Я люблю читать книги."], ["We go to work.", "Мы идём на работу."],
                ["She drinks tea in the morning.", "Она пьёт чай утром."], ["He wants to sleep.", "Он хочет спать."]],
      grammar: {
        title: "Present Simple: что мы делаем обычно",
        text: "Для привычек и фактов берут глагол как в словаре: I work, we read. Но с he, she, it добавляют -s: she works, he reads.",
        examples: [["I run every morning.", "Я бегаю каждое утро."], ["She studies English.", "Она учит английский."], ["He likes coffee.", "Ему нравится кофе."]]
      },
      quiz: [
        { q: "She ___ tea every day.", a: ["drink", "drinks", "drinking"], c: 1 },
        { q: "I ___ in an office.", a: ["works", "work", "working"], c: 1 },
        { q: "My brother ___ to sleep.", a: ["want", "wants", "is want"], c: 1 }
      ]
    },
    {
      id: "u7", icon: "🏙", title: "Город",
      words: [["street", "улица"], ["shop", "магазин"], ["car", "машина"], ["bus", "автобус"], ["park", "парк"],
              ["city", "город"], ["left", "налево"], ["right", "направо"], ["near", "рядом"], ["far", "далеко"]],
      phrases: [["Where is the shop?", "Где магазин?"], ["Turn left, please.", "Поверните налево, пожалуйста."],
                ["The park is near my house.", "Парк рядом с моим домом."], ["How do I get to the station?", "Как добраться до вокзала?"]],
      grammar: {
        title: "Вопросы: where, what, how",
        text: "Вопросительное слово ставят в начало, а потом меняют порядок: is или are идёт перед подлежащим. The shop is near → Where is the shop?",
        examples: [["Where is the bus?", "Где автобус?"], ["What is this street?", "Что это за улица?"], ["How are you?", "Как ты?"]]
      },
      quiz: [
        { q: "___ is the park? — It is near.", a: ["What", "Where", "Who"], c: 1 },
        { q: "Where ___ the shops?", a: ["is", "are", "am"], c: 1 },
        { q: "___ is your name?", a: ["What", "Where", "How"], c: 0 }
      ]
    },
    {
      id: "u8", icon: "📅", title: "Мой день",
      words: [["Monday", "понедельник"], ["Friday", "пятница"], ["Sunday", "воскресенье"], ["week", "неделя"], ["day", "день"],
              ["always", "всегда"], ["often", "часто"], ["never", "никогда"], ["early", "рано"], ["late", "поздно"]],
      phrases: [["I always get up early.", "Я всегда встаю рано."], ["On Sunday we rest.", "В воскресенье мы отдыхаем."],
                ["I often read in the evening.", "Я часто читаю вечером."], ["She is never late.", "Она никогда не опаздывает."]],
      grammar: {
        title: "Как часто: always, often, never",
        text: "Слова частоты ставят перед обычным глаголом (I always run), но после am, is, are (She is never late).",
        examples: [["I often drink tea.", "Я часто пью чай."], ["He never eats meat.", "Он никогда не ест мясо."], ["We are always happy.", "Мы всегда счастливы."]]
      },
      quiz: [
        { q: "Где правильно?", a: ["I always get up early.", "I get always up early.", "Always I get up early."], c: 0 },
        { q: "Где правильно?", a: ["She never is late.", "She is never late.", "Never she is late."], c: 1 },
        { q: "We ___ go to the park on Sunday.", a: ["often", "oftens", "is often"], c: 0 }
      ]
    },
    {
      id: "u9", icon: "💪", title: "Самочувствие",
      words: [["happy", "счастливый"], ["sad", "грустный"], ["tired", "уставший"], ["hungry", "голодный"], ["sick", "больной"],
              ["healthy", "здоровый"], ["strong", "сильный"], ["love", "любить"], ["feel", "чувствовать"], ["sport", "спорт"]],
      phrases: [["I am tired today.", "Я сегодня устал."], ["Are you hungry?", "Ты голоден?"],
                ["I don't feel well.", "Я плохо себя чувствую."], ["Sport is good for health.", "Спорт полезен для здоровья."]],
      grammar: {
        title: "Отрицание: not и don't",
        text: "С am, is, are просто добавляем not: I am not tired. С обычными глаголами ставим don't (с he, she — doesn't): I don't like, she doesn't like.",
        examples: [["I am not sad.", "Мне не грустно."], ["We don't eat meat.", "Мы не едим мясо."], ["He doesn't feel well.", "Он плохо себя чувствует."]]
      },
      quiz: [
        { q: "I ___ hungry.", a: ["don't", "am not", "not"], c: 1 },
        { q: "She ___ like coffee.", a: ["don't", "doesn't", "isn't"], c: 1 },
        { q: "We ___ go to work on Sunday.", a: ["don't", "doesn't", "aren't"], c: 0 }
      ]
    },
    {
      id: "u10", icon: "⏪", title: "Вчера и раньше",
      words: [["yesterday", "вчера"], ["was", "был, была"], ["were", "были"], ["went", "пошёл, ходил"], ["saw", "видел"],
              ["ate", "ел"], ["bought", "купил"], ["did", "сделал"], ["ago", "назад"], ["last week", "на прошлой неделе"]],
      phrases: [["I went to the park yesterday.", "Вчера я ходил в парк."], ["We saw a good film.", "Мы посмотрели хороший фильм."],
                ["Did you eat?", "Ты поел?"], ["I was at home last week.", "На прошлой неделе я был дома."]],
      grammar: {
        title: "Past Simple: прошедшее время",
        text: "К обычным глаголам добавляют -ed: work → worked. Частые глаголы неправильные, их запоминают: go → went, see → saw, eat → ate, buy → bought. В вопросе ставят did, а глагол берут как в словаре: Did you go?",
        examples: [["I worked yesterday.", "Вчера я работал."], ["She went home.", "Она пошла домой."], ["Did you see it?", "Ты это видел?"]]
      },
      quiz: [
        { q: "Yesterday I ___ to the shop.", a: ["go", "went", "goed"], c: 1 },
        { q: "___ you see the film?", a: ["Do", "Did", "Was"], c: 1 },
        { q: "They ___ at home last week.", a: ["was", "were", "are"], c: 1 }
      ]
    }
  ]
};

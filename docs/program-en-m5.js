// Месяц 5 (A2): Путешествия.
(function(){
const M = window.MD_PROGRAM.en.months[4];
M.weeks = [
  {
    t: "Транспорт и билеты",
    words: [
      ["journey", "поездка, путь", "джЁрни"], ["platform", "платформа", "плЭтформ"], ["timetable", "расписание", "тАймтэйбл"], ["single ticket", "билет в одну сторону", "сингл тИкит"], ["return ticket", "билет туда и обратно", "ритЁрн тИкит"],
      ["departure", "отправление, вылет", "дипАчэ"], ["arrival", "прибытие", "эрАйвл"], ["arrive", "прибывать, приезжать", "эрАйв"], ["leave", "уезжать, отправляться", "лив"], ["catch", "успеть (на транспорт)", "кэч"],
      ["miss", "опоздать (на транспорт)", "мис"], ["get on", "садиться (в транспорт)", "гет он"], ["get off", "выходить (из транспорта)", "гет оф"], ["passenger", "пассажир", "пЭсинджэ"], ["seat", "место, сиденье", "сит"],
      ["plane", "самолёт", "плэйн"], ["ship", "корабль", "шип"], ["ferry", "паром", "фЭри"], ["tram", "трамвай", "трэм"], ["underground", "метро (в Лондоне)", "Андэграунд"],
      ["flight", "рейс, полёт", "флайт"], ["boarding pass", "посадочный талон", "бОдинг пас"], ["luggage", "багаж", "лАгидж"], ["suitcase", "чемодан", "сУткейс"], ["on time", "вовремя", "он тайм"],
      ["delay", "задержка", "дилЭй"], ["direct", "прямой (без пересадок)", "дайрЭкт"], ["change trains", "делать пересадку (на поезде)", "чейндж трэйнз"], ["fare", "стоимость проезда", "фэа"], ["cancel", "отменять", "кЭнсл"]
    ],
    phrases: [["A return ticket to Oxford, please.", "Билет туда и обратно до Оксфорда, пожалуйста."], ["Which platform does the train leave from?", "С какой платформы отправляется поезд?"], ["Is this seat free?", "Это место свободно?"], ["Do I have to change trains?", "Мне нужно делать пересадку?"], ["The flight is delayed.", "Рейс задерживается."], ["What time does it arrive?", "Во сколько он прибывает?"]],
    grammar: {
      title: "Past Simple: вопросы и отрицания",
      text: "В вопросах и отрицаниях в Past Simple используем вспомогательный глагол did, а основной глагол возвращается в начальную форму: I went → Did you go? → I didn't go. Неправильно: Did you went? Вопрос с вопросительным словом: Where did you go? What time did the train leave? Краткие ответы: Yes, I did. / No, I didn't. Did и didn't одинаковы для всех лиц: She didn't catch the bus. Исключение — was / were: с ними did не нужен (Were you late? I wasn't tired).",
      examples: [["Did you buy a return ticket?", "Ты купил билет туда и обратно?"], ["We didn't miss the train.", "Мы не опоздали на поезд."], ["What time did the plane arrive?", "Во сколько прилетел самолёт?"], ["She didn't take her suitcase.", "Она не взяла свой чемодан."], ["Where did you get off?", "Где ты вышел?"]],
      quiz: [
        { q: "___ you catch the last bus?", a: ["Did", "Do", "Were"], c: 0 }, { q: "I didn't ___ the train.", a: ["miss", "missed", "misses"], c: 0 },
        { q: "What time ___ the flight arrive?", a: ["did", "was", "were"], c: 0 }, { q: "She ___ buy a return ticket. (не)", a: ["didn't", "wasn't", "doesn't"], c: 0 },
        { q: "Did they ___ by plane?", a: ["travel", "travelled", "travelling"], c: 0 }, { q: "Where did you ___ off the bus?", a: ["get", "got", "getting"], c: 0 },
        { q: "___ the train late? No, it was on time.", a: ["Was", "Did", "Were"], c: 0 }, { q: "Did you enjoy the journey? Yes, I ___.", a: ["did", "was", "enjoyed"], c: 0 }
      ]
    },
    read: {
      title: "Из Лондона в Эдинбург",
      text: "Last month I travelled from London to Edinburgh. I didn't want to fly, because the airport is far from the city centre and I don't like planes. So I took the train. I booked a return ticket online two weeks before the journey. It wasn't cheap: the fare was eighty pounds. My train left King's Cross station at nine o'clock from platform four. I didn't have much luggage, only a small suitcase and a backpack, so I found my seat easily. The journey took four and a half hours. It was a direct train, so I didn't have to change trains. There was a short delay near York, but we arrived on time anyway. I didn't sleep. I read a book and looked out of the window at the beautiful hills and the sea. Did I enjoy it? Yes, I did! Next time I'm going to take the night train.",
      gloss: [["easily", "легко"], ["took four and a half hours", "заняла четыре с половиной часа"], ["anyway", "всё равно"], ["looked out of the window", "смотрел в окно"], ["hills", "холмы"], ["night train", "ночной поезд"]],
      qs: [
        { q: "Почему автор не полетел на самолёте?", a: ["Аэропорт далеко от центра, и он не любит самолёты", "Билеты на самолёт были дороже", "Рейс отменили"], c: 0 },
        { q: "Сколько стоил билет?", a: ["80 фунтов", "18 фунтов", "40 фунтов"], c: 0 },
        { q: "Нужно ли было делать пересадку?", a: ["Нет, поезд был прямой", "Да, в Йорке", "Да, дважды"], c: 0 },
        { q: "Что автор делал в поезде?", a: ["Читал и смотрел в окно", "Спал", "Работал"], c: 0 }
      ]
    },
    listen: {
      lines: [["Clerk", "Good morning. Can I help you?"], ["Nina", "Yes, a return ticket to Oxford, please."], ["Clerk", "When are you coming back?"], ["Nina", "Tomorrow evening. How much is the fare?"], ["Clerk", "Twenty-four pounds. The next train leaves at ten fifteen from platform two."], ["Nina", "Is it a direct train?"], ["Clerk", "No, you have to change trains at Reading."], ["Nina", "Oh, I didn't know that. And the ten o'clock train? Did I miss it?"], ["Clerk", "Yes, I'm afraid you did. It left five minutes ago."], ["Nina", "Never mind. One return ticket, please."]],
      qs: [
        { q: "Куда едет Нина?", a: ["В Оксфорд", "В Рединг", "В Лондон"], c: 0 },
        { q: "Когда она возвращается?", a: ["Завтра вечером", "Сегодня вечером", "Через неделю"], c: 0 },
        { q: "С какой платформы отправляется поезд?", a: ["Со второй", "С десятой", "С четвёртой"], c: 0 },
        { q: "Что случилось с поездом в 10:00?", a: ["Он ушёл пять минут назад", "Его отменили", "Он опаздывает"], c: 0 }
      ]
    },
    speak: ["Did you buy a return ticket?", "We didn't miss the train.", "What time did the plane arrive?", "Where do I change trains?"],
    write: {
      trans: [
        ["Ты купил билет?", ["Did you buy a ticket", "Did you buy the ticket", "Have you bought a ticket", "Have you bought the ticket", "Did you buy tickets", "Did you buy the tickets"]],
        ["Мы не опоздали на поезд.", ["We didn't miss the train", "We did not miss the train", "We weren't late for the train", "We were not late for the train"]],
        ["Во сколько прибыл самолёт?", ["What time did the plane arrive", "When did the plane arrive", "What time did the plane land", "When did the plane land", "What time did the flight arrive", "When did the flight arrive"]],
        ["Она не взяла чемодан.", ["She didn't take a suitcase", "She didn't take the suitcase", "She didn't take her suitcase", "She did not take a suitcase", "She did not take the suitcase", "She did not take her suitcase"]]
      ],
      prompt: "Расскажи о последней поездке на поезде, автобусе или самолёте: куда ты ехал(а), как купил(а) билет, что было и чего не было в дороге. Используй вопросы и отрицания в прошедшем времени.",
      minWords: 55, use: ["didn't", "ticket", "arrived", "journey"],
      model: "Last summer I went to Kazan by train. I bought my ticket online, so I didn't have to stand in a queue at the station. The train left Moscow at ten in the evening. I didn't take much luggage, just one suitcase. The journey was long, but I slept well. Did we arrive on time? Yes, we did! We arrived in Kazan at nine in the morning, and my friend met me on the platform."
    }
  },
  {
    t: "Гостиница",
    words: [
      ["reception", "стойка регистрации, ресепшен", "рисЭпшн"], ["receptionist", "администратор", "рисЭпшэнист"], ["single room", "одноместный номер", "сингл рум"], ["double room", "двухместный номер", "дабл рум"], ["reservation", "бронь, бронирование", "рэзэвЭйшн"],
      ["check in", "заселяться, регистрироваться", "чек ин"], ["check out", "выселяться, выезжать", "чек аут"], ["lift", "лифт", "лифт"], ["floor", "этаж; пол", "флор"], ["stairs", "лестница", "стэаз"],
      ["view", "вид (из окна)", "вью"], ["balcony", "балкон", "бЭлкэни"], ["towel", "полотенце", "тАуэл"], ["pillow", "подушка", "пИлоу"], ["blanket", "одеяло", "блЭнкит"],
      ["air conditioning", "кондиционер", "эа кэндИшэнинг"], ["shower", "душ", "шАуэ"], ["Wi-Fi", "вай-фай", "вАй-фай"], ["key card", "ключ-карта", "ки кад"], ["included", "включённый", "инклУдид"],
      ["noise", "шум", "нойз"], ["staff", "персонал", "стаф"], ["cosy", "уютный", "кОузи"], ["dirty", "грязный", "дЁти"], ["broken", "сломанный", "брОукэн"],
      ["wake-up call", "звонок-будильник", "уЭйк-ап кол"], ["safe", "сейф", "сэйф"], ["fill in", "заполнять (бланк)", "фил ин"], ["form", "бланк, анкета", "форм"], ["passport", "паспорт", "пАспорт"]
    ],
    phrases: [["I have a reservation.", "У меня бронь."], ["Is breakfast included?", "Завтрак включён?"], ["What time is check-out?", "Во сколько нужно выехать?"], ["The air conditioning doesn't work.", "Кондиционер не работает."], ["Could I have another towel, please?", "Можно мне ещё одно полотенце?"], ["What's the Wi-Fi password?", "Какой пароль от вай-фая?"]],
    grammar: {
      title: "Past Continuous",
      text: "Past Continuous описывает действие, которое шло в какой-то момент в прошлом: At 9 pm I was having dinner. Форма: was / were + глагол с -ing: I was sleeping, they were waiting. Отрицание: wasn't / weren't + -ing. Вопрос: Were you sleeping? What were you doing? Часто Past Continuous — это «фон», а Past Simple — короткое событие, которое его прервало: I was having a shower when the phone rang. После while обычно идёт длительное действие: While we were checking in, it started to rain.",
      examples: [["I was sleeping when the alarm rang.", "Я спал, когда зазвонил будильник."], ["What were you doing at eight?", "Что ты делал в восемь?"], ["We were checking in when the lights went out.", "Мы заселялись, когда погас свет."], ["She wasn't watching TV.", "Она не смотрела телевизор."], ["While I was having a shower, someone knocked at the door.", "Пока я принимал душ, кто-то постучал в дверь."]],
      quiz: [
        { q: "At ten o'clock I ___ breakfast.", a: ["was having", "had having", "were having"], c: 0 }, { q: "They ___ waiting at reception.", a: ["were", "was", "did"], c: 0 },
        { q: "What ___ you doing at midnight?", a: ["were", "did", "was"], c: 0 }, { q: "I was sleeping when the phone ___.", a: ["rang", "was ringing", "rings"], c: 0 },
        { q: "___ we were checking out, it started to snow.", a: ["While", "During", "Then"], c: 0 }, { q: "She ___ watching TV. She was reading. (не)", a: ["wasn't", "weren't", "didn't"], c: 0 },
        { q: "___ he working when you called?", a: ["Was", "Were", "Did"], c: 0 }, { q: "The guests ___ dinner when the lights went out.", a: ["were having", "was having", "having"], c: 0 }
      ]
    },
    read: {
      title: "Ночь, которую не забыть",
      text: "Last spring my husband and I stayed in a small hotel by the sea. When we arrived, the receptionist was talking on the phone, so we waited for ten minutes. Then we filled in a form, showed our passports and got the key card for a double room on the fifth floor. The lift wasn't working, so we took the stairs! The room was cosy and it had a balcony with a wonderful view. But that night something strange happened. At two o'clock in the morning I was sleeping and my husband was reading when we heard a loud noise. Somebody was singing in the corridor! We called reception, but nobody answered. While my husband was putting on his clothes, the singing stopped. In the morning, while we were having breakfast, a man came to our table. 'I'm so sorry,' he said. 'It was my birthday last night.' He was the hotel manager!",
      gloss: [["showed", "показали"], ["wonderful", "чудесный"], ["strange", "странный"], ["happened", "случилось"], ["loud", "громкий"], ["corridor", "коридор"], ["nobody answered", "никто не ответил"]],
      qs: [
        { q: "Почему им пришлось ждать на ресепшене?", a: ["Администратор говорил по телефону", "Не было свободных номеров", "Они приехали слишком рано"], c: 0 },
        { q: "На каком этаже был номер?", a: ["На пятом", "На втором", "На первом"], c: 0 },
        { q: "Что делал муж в два часа ночи?", a: ["Читал", "Спал", "Пел"], c: 0 },
        { q: "Кто пел в коридоре?", a: ["Управляющий отелем", "Администратор", "Другой турист"], c: 0 }
      ]
    },
    listen: {
      lines: [["Receptionist", "Good evening. Welcome to the Park Hotel."], ["Mr Lee", "Good evening. I have a reservation. My name is David Lee."], ["Receptionist", "Yes, a single room for three nights. Can you fill in this form, please?"], ["Mr Lee", "Of course. Is breakfast included?"], ["Receptionist", "Yes, it is. Breakfast is from seven to ten in the restaurant on the first floor."], ["Mr Lee", "And what's the Wi-Fi password?"], ["Receptionist", "It's on your key card. Your room is 412. The lift is on the left."], ["Mr Lee", "Thanks. Oh, and can I have a wake-up call at six?"], ["Receptionist", "No problem. Sorry, were you waiting long? I was helping another guest."], ["Mr Lee", "Only a few minutes. It's fine."]],
      qs: [
        { q: "Какой номер забронировал мистер Ли?", a: ["Одноместный на три ночи", "Двухместный на три ночи", "Одноместный на одну ночь"], c: 0 },
        { q: "Где проходит завтрак?", a: ["В ресторане на первом этаже", "В номере", "В кафе рядом с отелем"], c: 0 },
        { q: "Где написан пароль от вай-фая?", a: ["На ключ-карте", "На стойке регистрации", "На двери номера"], c: 0 },
        { q: "Во сколько он хочет звонок-будильник?", a: ["В шесть", "В семь", "В десять"], c: 0 }
      ]
    },
    speak: ["I have a reservation for two nights.", "Is breakfast included?", "I was sleeping when the phone rang.", "What were you doing at eight o'clock?"],
    write: {
      trans: [
        ["Я спал, когда зазвонил телефон.", ["I was sleeping when the phone rang", "When the phone rang I was sleeping", "I was asleep when the phone rang", "When the phone rang I was asleep"]],
        ["Что ты делал в восемь часов?", ["What were you doing at eight o'clock", "What were you doing at eight", "What did you do at eight o'clock", "What did you do at eight"]],
        ["У меня бронь.", ["I have a reservation", "I've got a reservation", "I have a booking", "I've got a booking"]],
        ["Мы не смотрели телевизор.", ["We weren't watching TV", "We were not watching TV", "We didn't watch TV", "We did not watch TV", "We weren't watching television", "We didn't watch television"]]
      ],
      prompt: "Опиши, как ты останавливался(-ась) в гостинице: какой был номер, что было хорошо и что плохо. Расскажи, что ты делал(а), когда случилось что-то неожиданное.",
      minWords: 60, use: ["was", "were", "when", "room"],
      model: "Two years ago I stayed in a hotel in Saint Petersburg. I had a single room on the third floor with a view of the river. The room was small but clean, and the staff were very friendly. One evening I was having a shower when the water suddenly became cold. I called reception and a man came. While he was repairing the shower, I was waiting on the balcony. In the morning they gave me a free breakfast."
    }
  },
  {
    t: "История поездки",
    words: [
      ["tourist", "турист", "тУэрист"], ["guide", "гид, экскурсовод", "гайд"], ["tour", "экскурсия, тур", "туэ"], ["sightseeing", "осмотр достопримечательностей", "сАйтсиинг"], ["castle", "замок", "кАсл"],
      ["church", "церковь", "чёрч"], ["palace", "дворец", "пЭлис"], ["lake", "озеро", "лэйк"], ["river", "река", "рИвэ"], ["island", "остров", "Айлэнд"],
      ["forest", "лес", "фОрист"], ["coast", "побережье", "коуст"], ["souvenir", "сувенир", "сувэнИэ"], ["postcard", "открытка", "пОусткад"], ["camera", "фотоаппарат", "кЭмэрэ"],
      ["take photos", "фотографировать", "тэйк фОутоуз"], ["hill", "холм", "хил"], ["while", "пока, в то время как", "уайл"], ["during", "во время", "дьЮэринг"], ["finally", "наконец", "фАйнэли"],
      ["monument", "памятник", "мОньюмэнт"], ["waterfall", "водопад", "уОтэфол"], ["local", "местный", "лОукэл"], ["explore", "исследовать, осматривать", "иксплОр"], ["rent", "брать напрокат, арендовать", "рэнт"],
      ["tent", "палатка", "тэнт"], ["campsite", "кемпинг", "кЭмпсайт"], ["promise", "обещать; обещание", "прОмис"], ["backpack", "рюкзак", "бЭкпэк"], ["guidebook", "путеводитель", "гАйдбук"]
    ],
    phrases: [["What is there to see here?", "Что здесь можно посмотреть?"], ["How long does the tour take?", "Сколько длится экскурсия?"], ["Shall I take a photo of you?", "Тебя сфотографировать?"], ["I'll show you.", "Я тебе покажу."], ["It was a wonderful trip.", "Это была чудесная поездка."], ["I'll send you a postcard.", "Я пришлю тебе открытку."]],
    grammar: {
      title: "will для решений и обещаний",
      text: "Will + глагол используем, когда решаем что-то прямо в момент речи: It's cold. I'll take a jacket. Ещё will — для обещаний и предложений помощи: I'll send you a postcard. I'll help you with your bag. Отрицание: won't (= will not): I won't forget. Сравни с going to: I'm going to visit Rome — план уже есть; OK, I'll visit Rome — решаю сейчас. Вопрос Shall I…? — предложить свою помощь: Shall I take a photo of you? Will часто сокращается: I'll, we'll, she'll.",
      examples: [["I'll send you a postcard from Rome.", "Я пришлю тебе открытку из Рима."], ["It's raining. We'll take a taxi.", "Идёт дождь. Возьмём такси."], ["I won't forget your souvenir.", "Я не забуду про твой сувенир."], ["Shall I take a photo of you?", "Тебя сфотографировать?"], ["Don't worry, I'll help you.", "Не волнуйся, я тебе помогу."]],
      quiz: [
        { q: "The bag is heavy. I ___ help you.", a: ["will", "am", "going to"], c: 0 }, { q: "I promise I ___ forget. (не)", a: ["won't", "don't", "willn't"], c: 0 },
        { q: "It's hot. I think I'll ___ a swim.", a: ["have", "having", "to have"], c: 0 }, { q: "___ I take a photo of you?", a: ["Shall", "Do", "Am"], c: 0 },
        { q: "I'll ___ you a postcard!", a: ["send", "sending", "to send"], c: 0 }, { q: "We have no milk. OK, I ___ buy some.", a: ["will", "am", "was"], c: 0 },
        { q: "Don't worry, we ___ be late.", a: ["won't", "don't", "aren't"], c: 0 }, { q: "The tour is full today? Then we ___ go tomorrow.", a: ["will", "did", "were"], c: 0 }
      ]
    },
    read: {
      title: "Неделя на Байкале",
      text: "Last August my friend Pavel and I went to Lake Baikal. We rented a small car in Irkutsk and drove to the coast. For three nights we stayed at a campsite in the forest. The tent was small, but the view of the lake was wonderful. Every day was different. We explored the island of Olkhon with a local guide, climbed a hill, walked to an old wooden church and swam in the cold water. While we were walking in the forest, we suddenly saw a bear! Luckily, it ran away. On the last day I wanted to buy souvenirs, but I didn't have enough cash. 'Don't worry, I'll pay,' said Pavel. 'You can give me the money later.' I bought postcards for my family and some smoked fish. Before we left, I made a promise to the lake: 'I'll come back. I won't wait another ten years!' And I'm going to keep that promise.",
      gloss: [["drove", "поехали (на машине)"], ["wooden", "деревянный"], ["bear", "медведь"], ["luckily", "к счастью"], ["ran away", "убежал"], ["smoked fish", "копчёная рыба"], ["keep a promise", "сдержать обещание"]],
      qs: [
        { q: "Где друзья жили три ночи?", a: ["В палатке в кемпинге", "В отеле", "У местного гида"], c: 0 },
        { q: "Что неожиданного случилось в лесу?", a: ["Они увидели медведя", "Они заблудились", "Пошёл дождь"], c: 0 },
        { q: "Почему Павел заплатил за сувениры?", a: ["У автора не хватало наличных", "Это был подарок", "Автор потерял кошелёк"], c: 0 },
        { q: "Что пообещал автор?", a: ["Вернуться на Байкал", "Прислать Павлу деньги", "Написать книгу"], c: 0 }
      ]
    },
    listen: {
      lines: [["Guide", "Good morning! Are you joining the castle tour?"], ["Emma", "Yes, two tickets, please. What time does it start?"], ["Guide", "At eleven. It takes about three hours, with a stop at the lake."], ["Emma", "Great. Oh no, I left my camera at the hotel!"], ["Jack", "Don't worry. I'll take photos with my phone."], ["Emma", "Thanks. Is there a place to eat during the tour?"], ["Guide", "There's a small café near the palace. Or I'll show you a good local restaurant after the tour."], ["Jack", "That sounds perfect. Can we pay by card?"], ["Guide", "Sure. And here's a free guidebook for you."]],
      qs: [
        { q: "Во сколько начинается экскурсия?", a: ["В 11", "В 3", "В 10"], c: 0 },
        { q: "Что Эмма оставила в отеле?", a: ["Фотоаппарат", "Телефон", "Путеводитель"], c: 0 },
        { q: "Кто будет фотографировать?", a: ["Джек на телефон", "Гид", "Эмма"], c: 0 },
        { q: "Что гид даёт бесплатно?", a: ["Путеводитель", "Обед", "Открытку"], c: 0 }
      ]
    },
    speak: ["I'll send you a postcard.", "Don't worry, I'll help you.", "Shall I take a photo of you?", "I promise I won't be late."],
    write: {
      trans: [
        ["Я пришлю тебе открытку.", ["I'll send you a postcard", "I will send you a postcard"]],
        ["Не волнуйся, я тебе помогу.", ["Don't worry, I'll help you", "Do not worry, I will help you"]],
        ["Я не забуду.", ["I won't forget", "I will not forget", "I won't forget it", "I will not forget it"]],
        ["Тебя сфотографировать?", ["Shall I take a photo of you", "Shall I take your photo", "Shall I take a picture of you", "Shall I take your picture", "Should I take a photo of you", "Should I take your photo"]]
      ],
      prompt: "Расскажи историю своей поездки: куда ты ездил(а), что видел(а), что случилось неожиданно. В конце напиши, что ты обещаешь себе или другу (I'll…, I won't…).",
      minWords: 65, use: ["while", "suddenly", "I'll", "won't"],
      model: "Three years ago I went to Kaliningrad with my brother. We rented bikes and explored the coast. We visited an old castle and a beautiful church. One day, while we were riding along the sea, it suddenly started to rain. We were very wet, but a local woman invited us into her café and gave us hot tea. It was a wonderful day. Next summer I'll go there again, and I won't forget my umbrella!"
    }
  },
  {
    t: "Проблемы в пути",
    words: [
      ["problem", "проблема", "прОблэм"], ["lost property", "бюро находок", "лост прОпэти"], ["steal", "красть", "стил"], ["stolen", "украденный", "стОулэн"], ["wallet", "бумажник, кошелёк", "уОлит"],
      ["police", "полиция", "пэлИс"], ["report", "сообщать (о происшествии)", "рипОт"], ["embassy", "посольство", "Эмбэси"], ["visa", "виза", "вИзэ"], ["border", "граница", "бОдэ"],
      ["customs", "таможня", "кАстэмз"], ["security", "досмотр, охрана", "сикьЮрити"], ["document", "документ", "дОкьюмэнт"], ["ambulance", "скорая помощь", "Эмбьюлэнс"], ["break down", "сломаться (о машине)", "брэйк даун"],
      ["petrol", "бензин", "пЭтрэл"], ["flat tyre", "спущенное колесо", "флэт тАйэ"], ["traffic jam", "пробка (на дороге)", "трЭфик джэм"], ["storm", "шторм, гроза", "сторм"], ["pickpocket", "карманный вор", "пИкпокит"],
      ["insurance", "страховка", "иншУэрэнс"], ["worried", "обеспокоенный", "уАрид"], ["lose", "терять", "луз"], ["must", "должен", "маст"], ["have to", "приходится, нужно", "хэв ту"],
      ["mustn't", "нельзя", "мАснт"], ["allowed", "разрешено", "элАуд"], ["fine", "штраф", "файн"], ["garage", "автосервис", "гЭраж"], ["forget", "забывать", "фэгЕт"]
    ],
    phrases: [["Somebody stole my wallet.", "У меня украли кошелёк."], ["Where is the nearest police station?", "Где ближайший полицейский участок?"], ["Our car broke down.", "У нас сломалась машина."], ["I've lost my passport.", "Я потерял паспорт."], ["Can you help me, please?", "Помогите мне, пожалуйста."], ["Call an ambulance!", "Вызовите скорую!"]],
    grammar: {
      title: "must / have to",
      text: "Must и have to оба значат «должен», но есть разница. Must — когда говорящий сам считает что-то необходимым или это строгое правило: I must call my mum. Passengers must show their passports. Have to — когда так требуют обстоятельства или правила «извне»: I have to change trains in Paris. У must нет формы прошедшего времени, поэтому используем had to: We had to wait for three hours. А вот отрицания различаются сильно: mustn't = «нельзя»: You mustn't smoke here. Don't have to = «не обязательно»: You don't have to pay, it's free. Вопрос: Do I have to show my passport?",
      examples: [["You must show your passport at the border.", "На границе нужно показать паспорт."], ["We had to wait for three hours.", "Нам пришлось ждать три часа."], ["You mustn't smoke on the plane.", "В самолёте курить нельзя."], ["You don't have to pay. It's free.", "Платить не нужно. Это бесплатно."], ["Do I have to fill in this form?", "Мне нужно заполнять эту анкету?"]],
      quiz: [
        { q: "You ___ smoke here. It's not allowed.", a: ["mustn't", "don't have to", "haven't to"], c: 0 }, { q: "I lost my passport, so I ___ go to the embassy yesterday.", a: ["had to", "must", "have to"], c: 0 },
        { q: "You ___ pay for the museum. It's free.", a: ["don't have to", "mustn't", "must"], c: 0 }, { q: "___ I have to show my ticket?", a: ["Do", "Must", "Am"], c: 0 },
        { q: "She ___ to change trains in Berlin.", a: ["has", "have", "must"], c: 0 }, { q: "Passengers ___ wear seat belts.", a: ["must", "has to", "musts"], c: 0 },
        { q: "We didn't ___ wait long. The bus came quickly.", a: ["have to", "had to", "must"], c: 0 }, { q: "Our car broke down, so we ___ call a mechanic.", a: ["had to", "must", "have"], c: 0 }
      ]
    },
    read: {
      title: "Плохой день в Барселоне",
      text: "Last summer I had the worst day of my holiday in Barcelona. In the morning I was standing in a crowded metro when a pickpocket stole my wallet. My money, my credit card and my ID were all in it. Luckily, my passport was in the hotel safe. First I had to go to the police station to report the crime. I waited for two hours because there was a long queue of tourists with the same problem. The police officer was kind, but she said, 'You must cancel your credit card immediately.' I called my bank from her phone. Then I had to find some money. I didn't have to go to the embassy, because I still had my passport, but I had to ask my parents to send money from home. My travel insurance paid for most of it later. What did I learn? You mustn't keep everything in one wallet, and you must always have travel insurance!",
      gloss: [["ID", "удостоверение личности"], ["crime", "преступление"], ["the same", "такой же"], ["kind", "добрый"], ["immediately", "немедленно"], ["still", "всё ещё"], ["most of it", "большую часть"]],
      qs: [
        { q: "Где у автора украли кошелёк?", a: ["В метро", "В отеле", "На пляже"], c: 0 },
        { q: "Почему автору не пришлось идти в посольство?", a: ["Паспорт остался в сейфе отеля", "Посольство было закрыто", "Полиция сделала новый паспорт"], c: 0 },
        { q: "Что посоветовала сделать полицейская?", a: ["Сразу заблокировать карту", "Позвонить родителям", "Пойти в посольство"], c: 0 },
        { q: "Какой совет даёт автор?", a: ["Не держать всё в одном кошельке", "Не ездить в метро", "Не брать с собой карту"], c: 0 }
      ]
    },
    listen: {
      lines: [["Max", "Hello, is that Car Help? Our car broke down on the motorway."], ["Woman", "Where are you exactly?"], ["Max", "About ten kilometres from Bristol. I think we have a flat tyre."], ["Woman", "Is anybody hurt?"], ["Max", "No, we're fine. But it's raining and there's a lot of traffic."], ["Woman", "OK. You must stay in the car and put your lights on. A mechanic will be there in forty minutes."], ["Max", "Forty minutes? Do we have to pay for this?"], ["Woman", "No, you don't have to pay. It's in your insurance."], ["Max", "Great. Thank you very much."]],
      qs: [
        { q: "Что случилось с машиной?", a: ["Спустило колесо", "Закончился бензин", "Она попала в аварию"], c: 0 },
        { q: "Где они находятся?", a: ["В 10 км от Бристоля", "В центре Бристоля", "В 40 км от Бристоля"], c: 0 },
        { q: "Что им нужно делать до приезда механика?", a: ["Оставаться в машине с включёнными фарами", "Идти пешком до заправки", "Самим поменять колесо"], c: 0 },
        { q: "Нужно ли платить за помощь?", a: ["Нет, это входит в страховку", "Да, 40 фунтов", "Да, но позже"], c: 0 }
      ]
    },
    speak: ["I have to change trains in Paris.", "You mustn't smoke here.", "Somebody stole my wallet.", "Where is the nearest police station?"],
    write: {
      trans: [
        ["Мне нужно позвонить в банк.", ["I have to call the bank", "I must call the bank", "I need to call the bank", "I have to call my bank", "I must call my bank", "I need to call my bank", "I have to phone the bank", "I must phone the bank", "I need to phone the bank"]],
        ["Здесь нельзя курить.", ["You mustn't smoke here", "You must not smoke here", "You can't smoke here", "You cannot smoke here", "Smoking is not allowed here", "No smoking here"]],
        ["Нам пришлось долго ждать.", ["We had to wait for a long time", "We had to wait a long time", "We had to wait long"]],
        ["Вам не нужно платить.", ["You don't have to pay", "You do not have to pay", "You needn't pay", "You don't need to pay", "You do not need to pay"]]
      ],
      prompt: "Расскажи о проблеме, которая случилась с тобой или знакомым в поездке: что произошло, что пришлось сделать и какой совет ты дашь другим путешественникам (must, mustn't, have to).",
      minWords: 65, use: ["had to", "must", "mustn't", "lost"],
      model: "Two years ago my sister and I flew to Turkey. When we arrived at the airport, my sister's suitcase wasn't there. The airline lost it! We had to fill in a long form and wait for an hour. We didn't have any clothes, so we had to buy new T-shirts and swimsuits in the town. The suitcase came after three days. My advice is simple: you must keep important things in your hand luggage, and you mustn't forget your insurance documents."
    }
  }
];
M.exam = {
  read: {
    title: "Поездка в Прагу",
    text: "Last October Ivan and his wife Lena went on holiday to Prague. They didn't fly. They took a night train from Warsaw, because it was cheaper and more interesting. While they were sleeping, the train stopped for two hours because of a storm, so they arrived in Prague late. They had to take a taxi to the hotel, because they didn't want to miss the check-in. The hotel was beautiful, but there was a problem: the receptionist couldn't find their reservation. 'Don't worry,' she said finally. 'I'll give you a better room for the same price.' They got a big room with a balcony and a view of the old town. For the next five days they walked a lot, visited the castle and took hundreds of photos. On the last day Lena lost her phone in a café, but a waiter found it and called the hotel. 'Did you enjoy the trip?' Ivan's mother asked when they came home. 'Yes, we did,' said Lena. 'Next time we'll stay longer!'",
    gloss: [["because of", "из-за"], ["couldn't find", "не могла найти"], ["for the same price", "за ту же цену"], ["hundreds of", "сотни"], ["longer", "дольше"]],
    qs: [
      { q: "Почему они поехали на поезде?", a: ["Это было дешевле и интереснее", "Рейс отменили", "Они боятся летать"], c: 0 },
      { q: "Почему поезд опоздал?", a: ["Из-за шторма", "Сломался поезд", "Была забастовка"], c: 0 },
      { q: "Какая проблема была в отеле?", a: ["Не могли найти их бронь", "Не было горячей воды", "Номер был грязный"], c: 0 },
      { q: "Что потеряла Лена?", a: ["Телефон", "Кошелёк", "Паспорт"], c: 0 },
      { q: "Что Лена говорит в конце?", a: ["В следующий раз они останутся дольше", "Больше не поедут в Прагу", "В следующий раз полетят на самолёте"], c: 0 }
    ]
  },
  listen: {
    lines: [["Officer", "Good morning. Can I see your passport and boarding pass, please?"], ["Anna", "Here you are."], ["Officer", "Thank you. Did you pack your bag yourself?"], ["Anna", "Yes, I did."], ["Officer", "Is there any water in your bag?"], ["Anna", "Only a small bottle. Do I have to throw it away?"], ["Officer", "Yes, I'm afraid you must. You mustn't take more than one hundred millilitres."], ["Anna", "OK. Oh, and is my flight on time? I was having a coffee and I didn't hear the announcement."], ["Officer", "No, there's a delay of forty minutes. Your gate is number twelve."], ["Anna", "Thanks. I'll buy a magazine, then."]],
    qs: [
      { q: "Что офицер просит показать?", a: ["Паспорт и посадочный талон", "Билет и визу", "Страховку"], c: 0 },
      { q: "Кто собирал сумку Анны?", a: ["Она сама", "Её муж", "Об этом не сказано"], c: 0 },
      { q: "Что Анне нужно выбросить?", a: ["Бутылку воды", "Духи", "Еду"], c: 0 },
      { q: "Почему Анна не слышала объявление?", a: ["Пила кофе", "Говорила по телефону", "Спала"], c: 0 },
      { q: "На сколько задерживается рейс?", a: ["На 40 минут", "На 12 минут", "На час"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Ты опоздал на поезд?", ["Did you miss the train", "Did you miss your train", "Were you late for the train", "Have you missed the train"]],
      ["Я спал, когда ты позвонил.", ["I was sleeping when you called", "I was sleeping when you phoned", "I was sleeping when you rang", "I was asleep when you called", "I was asleep when you phoned", "When you called I was sleeping", "When you phoned I was sleeping"]],
      ["Я тебе помогу.", ["I'll help you", "I will help you"]],
      ["Нам пришлось взять такси.", ["We had to take a taxi", "We had to get a taxi", "We had to take a cab"]],
      ["Здесь нельзя фотографировать.", ["You mustn't take photos here", "You must not take photos here", "You mustn't take pictures here", "You must not take pictures here", "You can't take photos here", "You cannot take photos here", "You can't take pictures here", "You cannot take pictures here"]]
    ],
    prompt: "Напиши письмо другу о поездке, которая прошла не совсем гладко: как ты добирался(-ась), где жил(а), что случилось, что тебе пришлось сделать. Пообещай другу что-нибудь (I'll…).",
    minWords: 80, use: ["didn't", "was", "had to", "I'll"],
    model: "Hi Oleg! Last week I went to Minsk for a conference. I didn't fly, I took the train. The journey was fine, but the hotel was a problem. When I arrived, the receptionist was talking on the phone and she didn't see me for ten minutes. Then she said my room wasn't ready, so I had to wait in the café for two hours. In the evening, while I was having dinner, the lights went out in the whole hotel! But the city was beautiful and the people were very kind. I'll send you some photos tomorrow. Next time I'll take you with me! Your friend, Dima"
  },
  speak: ["Did you buy a return ticket?", "I was sleeping when the phone rang.", "Don't worry, I'll help you.", "You must show your passport.", "We had to wait for two hours."],
  grammar: [
    { q: "___ you visit the castle yesterday?", a: ["Did", "Were", "Was"], c: 0 }, { q: "We didn't ___ the flight.", a: ["miss", "missed", "missing"], c: 0 },
    { q: "I ___ having a shower when you called.", a: ["was", "were", "did"], c: 0 }, { q: "It's raining. I ___ take an umbrella.", a: ["will", "am", "was"], c: 0 },
    { q: "You ___ smoke on the plane.", a: ["mustn't", "don't have to", "haven't to"], c: 0 }, { q: "Yesterday I ___ to get up at five.", a: ["had", "must", "have"], c: 0 }
  ]
};
})();

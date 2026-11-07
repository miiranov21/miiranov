// Месяц 4 (A2): Покупки и сравнения.
(function(){
const M = window.MD_PROGRAM.en.months[3];
M.weeks = [
  {
    t: "Магазины и цены",
    words: [
      ["department store", "универмаг", "дипАртмэнт стор"], ["market", "рынок", "мАркит"], ["bakery", "пекарня, булочная", "бЭйкэри"], ["bookshop", "книжный магазин", "бУкшоп"], ["shopping centre", "торговый центр", "шОпинг сЭнтэ"],
      ["cash", "наличные", "кэш"], ["credit card", "кредитная карта", "крЭдит кард"], ["receipt", "чек", "рисИт"], ["change", "сдача; менять", "чейндж"], ["discount", "скидка", "дИскаунт"],
      ["sale", "распродажа", "сэйл"], ["cost", "стоить", "кост"], ["spend", "тратить", "спэнд"], ["save", "копить, экономить", "сэйв"], ["queue", "очередь", "кью"],
      ["cashier", "кассир", "кэшИэ"], ["coin", "монета", "койн"], ["quality", "качество", "куОлити"], ["online", "в интернете, онлайн", "онлАйн"], ["pound", "фунт (деньги)", "паунд"],
      ["better", "лучше", "бЭтэ"], ["worse", "хуже", "уёрс"], ["best", "лучший, самый хороший", "бэст"], ["worst", "худший", "уёрст"], ["modern", "современный", "мОдэрн"],
      ["popular", "популярный", "пОпьюлэ"], ["open", "открытый; открывать", "Оупэн"], ["closed", "закрытый", "клоузд"], ["compare", "сравнивать", "кэмпЭа"], ["than", "чем (при сравнении)", "зэн"]
    ],
    phrases: [["How much does it cost?", "Сколько это стоит?"], ["Can I pay by card?", "Можно оплатить картой?"], ["Is there a discount?", "Есть скидка?"], ["Can I have the receipt, please?", "Дайте, пожалуйста, чек."], ["It's cheaper than in the market.", "Это дешевле, чем на рынке."], ["What time does the shop close?", "Во сколько закрывается магазин?"]],
    grammar: {
      title: "Сравнительная и превосходная степень",
      text: "Чтобы сравнить два предмета, к коротким прилагательным добавляем -er и ставим than (чем): cheap → cheaper than, big → bigger than. Если прилагательное оканчивается на -y, y меняется на i: busy → busier, easy → easier. С длинными прилагательными (из двух-трёх слогов и больше) используем more: expensive → more expensive than. Превосходная степень (самый) — the + -est для коротких слов (the cheapest, the biggest) и the most для длинных (the most popular). Исключения нужно запомнить: good → better → the best, bad → worse → the worst, far → further → the furthest. Пример: The market is cheaper than the supermarket, but the department store is the most expensive.",
      examples: [["The market is cheaper than the supermarket.", "Рынок дешевле, чем супермаркет."], ["This bag is more expensive than that one.", "Эта сумка дороже, чем та."], ["It's the biggest shopping centre in the city.", "Это самый большой торговый центр в городе."], ["This is the worst shop in town.", "Это худший магазин в городе."], ["Online shops are more popular now.", "Интернет-магазины сейчас популярнее."]],
      quiz: [
        { q: "The market is ___ than the shop. (дешевле)", a: ["cheaper", "more cheap", "cheapest"], c: 0 }, { q: "This is the ___ shopping centre in the city.", a: ["biggest", "bigger", "most big"], c: 0 },
        { q: "Shoes here are ___ expensive than online.", a: ["more", "most", "much"], c: 0 }, { q: "This café is ___ than that one. (лучше)", a: ["better", "gooder", "best"], c: 0 },
        { q: "It's the ___ popular brand in Russia.", a: ["most", "more", "much"], c: 0 }, { q: "The bakery is ___ than the supermarket. (ближе)", a: ["nearer", "more near", "nearest"], c: 0 },
        { q: "Today was the ___ day of my life! (худший)", a: ["worst", "worse", "baddest"], c: 0 }, { q: "My bag is heavier ___ yours.", a: ["than", "that", "then"], c: 0 }
      ]
    },
    read: {
      title: "Где делать покупки в моём городе",
      text: "There are many places to shop in my town, and I often compare them. The market is the cheapest place for fruit and vegetables. It is open every day except Monday, and the food there is fresher than in the supermarket. But you can only pay in cash, and there is often a long queue. The new shopping centre is bigger and more modern than the market. It has a cinema, cafés and more than fifty shops. It is the most popular place for young people, but the prices are higher. Last week there was a big sale, and I bought a jacket with a forty per cent discount. My favourite shop is a small bookshop near my house. It isn't the cheapest, but the quality of the books is the best, and the people who work there are very friendly. Of course, many people buy things online now. It is often cheaper and faster, but I like to see things before I buy them. And I always keep the receipt!",
      gloss: [["except", "кроме"], ["fresher", "свежее"], ["higher", "выше"], ["per cent", "процент"], ["favourite", "любимый"], ["friendly", "дружелюбный"], ["keep", "хранить, оставлять"]],
      qs: [
        { q: "Где дешевле всего покупать фрукты и овощи?", a: ["На рынке", "В торговом центре", "В интернете"], c: 0 },
        { q: "Как можно платить на рынке?", a: ["Только наличными", "Только картой", "Наличными или картой"], c: 0 },
        { q: "Какую скидку получил автор на куртку?", a: ["40%", "50%", "14%"], c: 0 },
        { q: "Почему автор не любит покупать в интернете?", a: ["Хочет увидеть вещь перед покупкой", "Там дороже", "Там медленнее"], c: 0 }
      ]
    },
    listen: {
      lines: [["Anna", "Look at these two phones. Which one is better?"], ["Max", "The black one is newer and faster, but it costs four hundred pounds."], ["Anna", "And the white one?"], ["Max", "It's cheaper. Only two hundred and fifty. There's a discount this week."], ["Anna", "Is the quality worse?"], ["Max", "Not really. The camera is a bit worse, but it's a popular brand."], ["Anna", "I don't want to spend too much. I'm saving for a holiday."], ["Max", "Then buy the white one. Can you pay by credit card here?"], ["Assistant", "Yes, of course. Or you can pay in cash."], ["Anna", "By card, please. Can I have the receipt?"]],
      qs: [
        { q: "Сколько стоит чёрный телефон?", a: ["400 фунтов", "250 фунтов", "200 фунтов"], c: 0 },
        { q: "Что хуже у белого телефона?", a: ["Камера", "Цвет", "Марка"], c: 0 },
        { q: "На что копит Анна?", a: ["На отпуск", "На машину", "На квартиру"], c: 0 },
        { q: "Как Анна платит?", a: ["Картой", "Наличными", "Онлайн"], c: 0 }
      ]
    },
    speak: ["This shop is cheaper than the market.", "It's the most popular shopping centre in the city.", "Can I pay by credit card?", "How much does it cost?"],
    write: {
      trans: [
        ["Рынок дешевле, чем супермаркет.", ["The market is cheaper than the supermarket"]],
        ["Это самый большой магазин в городе.", ["It is the biggest shop in the city", "This is the biggest shop in the city", "It is the biggest shop in town", "This is the biggest shop in town", "It is the biggest store in the city", "This is the biggest store in the city", "It is the largest shop in the city", "This is the largest shop in the city", "It is the biggest shop in the town", "This is the biggest shop in the town"]],
        ["Сколько это стоит?", ["How much does it cost", "How much is it", "How much is this", "How much does this cost"]],
        ["Можно заплатить наличными?", ["Can I pay in cash", "Can I pay cash", "Can I pay by cash", "Can we pay in cash", "May I pay in cash", "Can I pay with cash"]]
      ],
      prompt: "Сравни два магазина или торговых центра в твоём городе: где дешевле, где лучше качество, где больше людей. Какой магазин, по-твоему, самый лучший?",
      minWords: 50, use: ["cheaper", "than", "the most", "better"],
      model: "There are two big shops near my house. The first one is a supermarket. It is cheaper than the second shop, and it is open every day until eleven. But the queues are long and the quality of the fruit is not very good. The second shop is smaller and more expensive, but the food is fresher and better. I think the bakery in my street is the most popular shop in our area. Its bread is the best in town!"
    }
  },
  {
    t: "Одежда и размеры",
    words: [
      ["size", "размер", "сайз"], ["medium", "средний (размер)", "мИдиэм"], ["large", "большой (размер)", "ладж"], ["try on", "примерять", "трай он"], ["fitting room", "примерочная", "фИтинг рум"],
      ["fit", "подходить по размеру", "фит"], ["suit", "идти (кому-то); костюм", "сут"], ["tight", "тесный, узкий", "тайт"], ["loose", "свободный, широкий", "лус"], ["long", "длинный", "лонг"],
      ["sweater", "свитер", "суЭтэ"], ["socks", "носки", "сокс"], ["belt", "ремень, пояс", "бэлт"], ["scarf", "шарф", "скаф"], ["gloves", "перчатки", "главз"],
      ["trainers", "кроссовки", "трЭйнэз"], ["sandals", "сандалии", "сЭндлз"], ["pocket", "карман", "пОкит"], ["button", "пуговица", "бАтн"], ["cotton", "хлопок, хлопковый", "кОтн"],
      ["wool", "шерсть, шерстяной", "вул"], ["leather", "кожа, кожаный", "лЭзэ"], ["fashionable", "модный", "фЭшнэбл"], ["comfortable", "удобный", "кАмфтэбл"], ["smart", "нарядный, элегантный", "смат"],
      ["casual", "повседневный (о стиле)", "кЭжуэл"], ["too", "слишком", "ту"], ["enough", "достаточно", "инАф"], ["grey", "серый", "грэй"], ["brown", "коричневый", "браун"]
    ],
    phrases: [["Can I try this on?", "Можно это примерить?"], ["Where is the fitting room?", "Где примерочная?"], ["What size are you?", "Какой у вас размер?"], ["It's too small for me.", "Мне это слишком мало."], ["Have you got a larger size?", "У вас есть размер побольше?"], ["It really suits you.", "Тебе это очень идёт."]],
    grammar: {
      title: "too и enough",
      text: "Too значит «слишком» и ставится перед прилагательным: These jeans are too tight. Too говорит о проблеме: вещь не подходит, её трудно купить или надеть. Enough значит «достаточно» и ставится после прилагательного: This coat isn't warm enough. А с существительным enough стоит перед ним: I don't have enough money. Можно добавить, для кого или для чего: It's too big for me. It's too expensive to buy. Не путай too и very: very — просто «очень» (This dress is very nice), а too — «слишком, больше, чем нужно» (This dress is too long).",
      examples: [["This shirt is too small for me.", "Эта рубашка мне слишком мала."], ["The jacket isn't big enough.", "Куртка недостаточно большая."], ["These shoes are too expensive.", "Эти туфли слишком дорогие."], ["I don't have enough money.", "У меня недостаточно денег."], ["Is it warm enough for winter?", "Она достаточно тёплая для зимы?"]],
      quiz: [
        { q: "These trousers are ___ long. I need a shorter pair.", a: ["too", "enough", "much"], c: 0 }, { q: "This coat isn't warm ___.", a: ["enough", "too", "very"], c: 0 },
        { q: "I don't have ___ money for this dress.", a: ["enough", "too", "very"], c: 0 }, { q: "The jeans are too tight ___ me.", a: ["for", "to", "at"], c: 0 },
        { q: "Is this sweater big ___ for you?", a: ["enough", "too", "so"], c: 0 }, { q: "It's ___ expensive. I can't buy it.", a: ["too", "enough", "very much"], c: 0 },
        { q: "The shoes are nice, but they aren't ___. (достаточно удобные)", a: ["comfortable enough", "enough comfortable", "too comfortable"], c: 0 }, { q: "She is ___ young to drive.", a: ["too", "enough", "much"], c: 0 }
      ]
    },
    read: {
      title: "Одежда для работы",
      text: "Last Saturday I went to the shopping centre because I needed new clothes for work. First I tried on a grey suit. The jacket was fine, but the trousers were too long and too tight. The shop assistant brought a larger size, but it was the wrong colour. Then I found a nice brown leather belt and some cotton shirts. They were smart enough for the office and not too expensive. Shoes were the biggest problem. I wear size forty-four, and the black shoes I liked were only in forty-two. I tried on some trainers too, but they weren't comfortable enough for long walks. In the end I bought a pair of brown shoes. They were more expensive than I wanted, but they fit perfectly. At home my wife looked at everything and said, 'The shirts are great, but you forgot socks again!'",
      gloss: [["needed", "был нужен"], ["brought", "принёс"], ["wrong", "не тот, неправильный"], ["pair", "пара"], ["perfectly", "идеально"], ["in the end", "в конце концов"], ["forgot", "забыл"]],
      qs: [
        { q: "Что было не так с брюками?", a: ["Слишком длинные и узкие", "Слишком короткие", "Не тот цвет"], c: 0 },
        { q: "Почему рубашки подошли?", a: ["Достаточно нарядные и не слишком дорогие", "Они были на распродаже", "Они из шерсти"], c: 0 },
        { q: "Какой размер обуви носит автор?", a: ["44", "42", "40"], c: 0 },
        { q: "Что автор забыл купить?", a: ["Носки", "Ремень", "Галстук"], c: 0 }
      ]
    },
    listen: {
      lines: [["Assistant", "Hello, can I help you?"], ["Kate", "Yes, I'm looking for a warm sweater. Do you have this one in medium?"], ["Assistant", "Yes, here you are. The fitting room is over there."], ["Kate", "Thanks. Hmm, it's too short for me. Have you got a large?"], ["Assistant", "Sorry, we haven't got large in grey. Only in pink or brown."], ["Kate", "Brown is OK. Can I try it on?"], ["Assistant", "Of course. How is it?"], ["Kate", "It's perfect! It's long enough and the wool is really soft. How much is it?"], ["Assistant", "Forty-five pounds, but there's a ten per cent discount today."], ["Kate", "Great, I'll take it."]],
      qs: [
        { q: "Что ищет Кейт?", a: ["Тёплый свитер", "Шарф", "Пальто"], c: 0 },
        { q: "Что не так со свитером размера M?", a: ["Слишком короткий", "Слишком широкий", "Слишком дорогой"], c: 0 },
        { q: "Какого цвета свитер она берёт?", a: ["Коричневый", "Серый", "Розовый"], c: 0 },
        { q: "Какая скидка сегодня?", a: ["10%", "45%", "20%"], c: 0 }
      ]
    },
    speak: ["Can I try this on?", "These jeans are too tight.", "This coat isn't warm enough.", "Have you got this in a larger size?"],
    write: {
      trans: [
        ["Эти джинсы слишком узкие.", ["These jeans are too tight", "These jeans are too narrow"]],
        ["Можно это примерить?", ["Can I try this on", "Can I try it on", "May I try this on", "May I try it on", "Could I try this on", "Could I try it on"]],
        ["Куртка недостаточно тёплая.", ["The jacket isn't warm enough", "The jacket is not warm enough", "The jacket's not warm enough"]],
        ["У меня недостаточно денег.", ["I don't have enough money", "I haven't got enough money", "I do not have enough money", "I have not got enough money"]]
      ],
      prompt: "Расскажи, как ты покупал(а) одежду: что примерял(а), что было слишком большим, маленьким или дорогим и что ты в итоге купил(а).",
      minWords: 55, use: ["too", "enough", "tried on", "size"],
      model: "Last month I needed a new coat for winter. I went to a big department store and tried on five coats. The first one was too short and the second one wasn't warm enough. I liked a grey wool coat, but it was too expensive for me. Finally I found a dark blue coat in my size. It was comfortable, warm enough for cold days and not very expensive. I also bought a scarf and gloves."
    }
  },
  {
    t: "Кафе и ресторан",
    words: [
      ["menu", "меню", "мЭнью"], ["order", "заказывать; заказ", "Одэ"], ["bill", "счёт (в кафе)", "бил"], ["tip", "чаевые", "тип"], ["starter", "закуска", "стАтэ"],
      ["main course", "основное блюдо", "мэйн кос"], ["dessert", "десерт", "дизЁрт"], ["dish", "блюдо", "диш"], ["salad", "салат", "сЭлэд"], ["steak", "стейк", "стэйк"],
      ["pasta", "паста, макароны", "пЭстэ"], ["sandwich", "бутерброд, сэндвич", "сЭнуич"], ["ice cream", "мороженое", "айс крим"], ["glass", "стакан, бокал", "глас"], ["bottle", "бутылка", "бОтл"],
      ["plate", "тарелка", "плэйт"], ["fork", "вилка", "фок"], ["knife", "нож", "найф"], ["spoon", "ложка", "спун"], ["napkin", "салфетка", "нЭпкин"],
      ["waitress", "официантка", "уЭйтрис"], ["book a table", "заказать столик", "бук э тэйбл"], ["delicious", "очень вкусный", "дилИшэс"], ["spicy", "острый (о еде)", "спАйси"], ["sweet", "сладкий", "суит"],
      ["fresh", "свежий", "фрэш"], ["vegetarian", "вегетарианский; вегетарианец", "вэджэтЭэриэн"], ["sparkling", "газированный", "спАклинг"], ["lunch", "обед", "ланч"], ["dinner", "ужин", "дИнэ"]
    ],
    phrases: [["A table for two, please.", "Столик на двоих, пожалуйста."], ["Can I see the menu, please?", "Можно меню, пожалуйста?"], ["Are you ready to order?", "Вы готовы сделать заказ?"], ["I'd like the soup, please.", "Мне, пожалуйста, суп."], ["Would you like a dessert?", "Хотите десерт?"], ["Can we have the bill, please?", "Принесите, пожалуйста, счёт."]],
    grammar: {
      title: "I'd like, would you like",
      text: "I'd like (= I would like) — вежливое «я бы хотел(а)». Его используем в кафе, ресторане и магазине вместо грубоватого I want: I'd like a coffee, please. После I'd like идёт существительное или to + глагол: I'd like to book a table. Вопрос Would you like…? — вежливое предложение: Would you like some tea? Отвечаем Yes, please или No, thank you. Would you like to…? — приглашение: Would you like to have dinner with us? Не путай: Do you like coffee? — «Ты любишь кофе (вообще)?», а Would you like a coffee? — «Хочешь кофе (сейчас)?»",
      examples: [["I'd like a glass of water, please.", "Мне, пожалуйста, стакан воды."], ["Would you like a dessert?", "Хотите десерт?"], ["We'd like to book a table for two.", "Мы бы хотели заказать столик на двоих."], ["Would you like to come for dinner?", "Хочешь прийти на ужин?"], ["What would you like to drink?", "Что вы будете пить?"]],
      quiz: [
        { q: "I'd ___ a cup of tea, please.", a: ["like", "likes", "to like"], c: 0 }, { q: "___ you like some dessert?", a: ["Would", "Do", "Are"], c: 0 },
        { q: "We'd like ___ a table for four.", a: ["to book", "book", "booking"], c: 0 }, { q: "What would you like ___ drink?", a: ["to", "for", "that"], c: 0 },
        { q: "Would you like a coffee? Yes, ___.", a: ["please", "I do", "I like"], c: 0 }, { q: "___ like the steak, please. (Я бы хотел)", a: ["I'd", "I", "I'm"], c: 0 },
        { q: "___ you like pizza? Yes, it's my favourite food. (вообще)", a: ["Do", "Would", "Are"], c: 0 }, { q: "Would you like ___ with us tonight?", a: ["to come", "come", "coming"], c: 0 }
      ]
    },
    read: {
      title: "Ужин в итальянском ресторане",
      text: "Last Friday my husband and I had dinner at Luigi's, a small Italian restaurant near the river. We booked a table for eight o'clock. The waitress was very friendly. 'Would you like something to drink?' she asked. I ordered sparkling water and my husband had a glass of red wine. For the starter we shared a fresh tomato salad. For the main course I had pasta with vegetables, because I'm vegetarian, and my husband chose a steak. The food was delicious, but his steak was a bit spicy. Then the waitress asked, 'Would you like a dessert?' We were full, but we said yes to ice cream. It was the best ice cream in town! The bill was sixty-two pounds. It wasn't cheap, but we left a tip because the service was excellent. Next time I'd like to try their pizza.",
      gloss: [["shared", "разделили (на двоих)"], ["wine", "вино"], ["chose", "выбрал"], ["full", "сытые"], ["left", "оставили"], ["service", "обслуживание"], ["excellent", "отличный"]],
      qs: [
        { q: "На какое время они заказали столик?", a: ["На 8 часов", "На 7 часов", "На 9 часов"], c: 0 },
        { q: "Почему автор заказала пасту с овощами?", a: ["Она вегетарианка", "Стейк был острым", "Это было самое дешёвое блюдо"], c: 0 },
        { q: "Что они взяли на десерт?", a: ["Мороженое", "Торт", "Ничего"], c: 0 },
        { q: "Сколько стоил ужин?", a: ["62 фунта", "26 фунтов", "52 фунта"], c: 0 }
      ]
    },
    listen: {
      lines: [["Waiter", "Good afternoon. Are you ready to order?"], ["Olga", "Yes. I'd like the chicken sandwich, please."], ["Waiter", "Would you like a salad with it?"], ["Olga", "No, thank you. But I'd like some soup. Is the tomato soup spicy?"], ["Waiter", "No, it isn't. And for you, sir?"], ["Ivan", "I'd like the fish of the day with rice."], ["Waiter", "And what would you like to drink?"], ["Ivan", "Two glasses of orange juice, please."], ["Waiter", "Would you like to see the dessert menu later?"], ["Olga", "Yes, please. And can we have the bill after that?"]],
      qs: [
        { q: "Что заказывает Ольга?", a: ["Сэндвич с курицей и суп", "Салат и суп", "Рыбу с рисом"], c: 0 },
        { q: "Острый ли томатный суп?", a: ["Нет", "Да", "Немного"], c: 0 },
        { q: "Что они будут пить?", a: ["Апельсиновый сок", "Газированную воду", "Кофе"], c: 0 },
        { q: "Что Ольга хочет посмотреть позже?", a: ["Меню десертов", "Счёт за напитки", "Винную карту"], c: 0 }
      ]
    },
    speak: ["I'd like to book a table for two.", "Would you like something to drink?", "I'd like the fish, please.", "Can we have the bill, please?"],
    write: {
      trans: [
        ["Я бы хотел стакан воды.", ["I'd like a glass of water", "I would like a glass of water", "I'd like a glass of water please", "I would like a glass of water please"]],
        ["Хотите десерт?", ["Would you like a dessert", "Would you like dessert", "Would you like some dessert", "Do you want a dessert", "Do you want dessert", "Do you want some dessert"]],
        ["Мы бы хотели заказать столик на двоих.", ["We'd like to book a table for two", "We would like to book a table for two", "We'd like to reserve a table for two", "We would like to reserve a table for two"]],
        ["Принесите, пожалуйста, счёт.", ["Can we have the bill, please", "Can I have the bill, please", "The bill, please", "Could we have the bill, please", "Could I have the bill, please", "Can we have the bill", "Can I have the bill", "Please bring the bill", "Bring the bill, please", "Bring me the bill, please", "Bring us the bill, please"]]
      ],
      prompt: "Напиши диалог в кафе или ресторане: ты заказываешь еду и напитки, а официант предлагает тебе что-то ещё. Используй I'd like и Would you like.",
      minWords: 55, use: ["I'd like", "Would you like", "menu", "bill"],
      model: "Waiter: Good evening. Here is the menu. Would you like something to drink? Me: Yes, I'd like a glass of sparkling water, please. Waiter: Are you ready to order? Me: Yes. For the starter I'd like the tomato soup, and for the main course I'd like the chicken with rice. Waiter: Would you like a salad with it? Me: No, thank you. Waiter: Would you like a dessert? Me: Yes, the chocolate cake, please. And can I have the bill, please?"
    }
  },
  {
    t: "Планы",
    words: [
      ["plan", "план; планировать", "плэн"], ["tomorrow", "завтра", "тэмОроу"], ["next", "следующий", "нэкст"], ["tonight", "сегодня вечером", "тэнАйт"], ["soon", "скоро", "сун"],
      ["later", "позже", "лЭйтэ"], ["future", "будущее", "фьЮчэ"], ["learn", "учить, узнавать", "лёрн"], ["move", "переезжать", "мув"], ["get married", "пожениться, выйти замуж", "гет мЭрид"],
      ["course", "курс (обучения)", "кос"], ["exam", "экзамен", "игзЭм"], ["pass", "сдать (экзамен)", "пас"], ["fail", "провалить (экзамен)", "фэйл"], ["decide", "решать", "дисАйд"],
      ["hope", "надеяться; надежда", "хоуп"], ["dream", "мечта; мечтать", "дрим"], ["idea", "идея", "айдИэ"], ["paint", "красить", "пэйнт"], ["build", "строить", "билд"],
      ["garden", "сад", "гАдэн"], ["invite", "приглашать", "инвАйт"], ["wedding", "свадьба", "уЭдинг"], ["celebrate", "праздновать", "сЭлибрэйт"], ["birthday", "день рождения", "бЁсдэй"],
      ["present", "подарок", "прЭзэнт"], ["lose weight", "похудеть", "луз уэйт"], ["give up", "бросить (привычку)", "гив ап"], ["driving test", "экзамен по вождению", "дрАйвинг тэст"], ["sure", "уверенный", "шуэ"]
    ],
    phrases: [["What are you going to do tonight?", "Что ты собираешься делать сегодня вечером?"], ["I'm going to stay at home.", "Я собираюсь остаться дома."], ["Have you got any plans for the weekend?", "У тебя есть планы на выходные?"], ["See you tomorrow!", "До завтра!"], ["That's a good idea!", "Хорошая идея!"], ["I'm not sure yet.", "Я пока не уверен."]],
    grammar: {
      title: "be going to",
      text: "Be going to + глагол — так говорим о планах и намерениях, которые уже решены: I'm going to learn Spanish next year. Форма: am / is / are + going to + глагол: She's going to move to Moscow. Отрицание: I'm not going to buy a car. Вопрос: Are you going to celebrate your birthday? What are you going to do tomorrow? Ещё going to используем, когда видим, что что-то вот-вот случится: Look at those clouds! It's going to rain. С going to часто употребляют слова tomorrow, tonight, next week, next year, soon.",
      examples: [["I'm going to learn English this year.", "В этом году я собираюсь учить английский."], ["We're going to paint the kitchen.", "Мы собираемся покрасить кухню."], ["She isn't going to come tonight.", "Она не собирается приходить сегодня вечером."], ["What are you going to do tomorrow?", "Что ты собираешься делать завтра?"], ["Look at the sky! It's going to rain.", "Посмотри на небо! Сейчас пойдёт дождь."]],
      quiz: [
        { q: "I ___ going to visit my parents tomorrow.", a: ["am", "is", "are"], c: 0 }, { q: "They're going ___ a new flat.", a: ["to buy", "buy", "buying"], c: 0 },
        { q: "___ she going to come to the party?", a: ["Is", "Does", "Are"], c: 0 }, { q: "We ___ going to move. We like our house. (не)", a: ["aren't", "don't", "isn't"], c: 0 },
        { q: "What ___ you going to do next weekend?", a: ["are", "do", "will"], c: 0 }, { q: "Look at the clouds! It's ___ rain.", a: ["going to", "go to", "going"], c: 0 },
        { q: "He's going to ___ smoking.", a: ["give up", "gives up", "giving up"], c: 0 }, { q: "My sister ___ going to get married next summer.", a: ["is", "are", "am"], c: 0 }
      ]
    },
    read: {
      title: "Мои планы на следующий год",
      text: "Every January I make a list of plans, and this year is no different. Here are my big ideas. First, I'm going to pass my driving test. I failed it last year because I made too many mistakes, but now I'm taking lessons twice a week. Second, my girlfriend and I are going to get married in June! We aren't going to have a big wedding. We're going to invite only our families and close friends, and we're going to celebrate in my parents' garden. Third, we're going to move to a bigger flat. Our flat is too small for two people and a dog. We're going to paint the walls and repair the old kitchen ourselves. I also hope to learn some Spanish, because we're going to spend our honeymoon in Spain. I'm not sure I'm going to have enough time, but I'm going to try!",
      gloss: [["list", "список"], ["no different", "не исключение"], ["lessons", "уроки"], ["close friends", "близкие друзья"], ["ourselves", "сами"], ["honeymoon", "медовый месяц"]],
      qs: [
        { q: "Почему автор не сдал экзамен по вождению в прошлом году?", a: ["Сделал слишком много ошибок", "Опоздал на экзамен", "Не ходил на уроки"], c: 0 },
        { q: "Где они будут праздновать свадьбу?", a: ["В саду у родителей", "В ресторане", "В Испании"], c: 0 },
        { q: "Почему они хотят переехать?", a: ["Квартира слишком маленькая", "Квартира слишком дорогая", "Далеко от работы"], c: 0 },
        { q: "Зачем автор хочет учить испанский?", a: ["Медовый месяц будет в Испании", "Для работы", "Его девушка испанка"], c: 0 }
      ]
    },
    listen: {
      lines: [["Sam", "Hi, Lena! What are you going to do this weekend?"], ["Lena", "I'm going to paint my bedroom. It's going to be yellow!"], ["Sam", "Nice! Are you going to do it alone?"], ["Lena", "No, my brother is going to help me. What about you?"], ["Sam", "It's my birthday on Saturday. I'm going to celebrate at home."], ["Lena", "Really? Are you going to invite many guests?"], ["Sam", "Only ten people. I'm going to cook dinner for everybody."], ["Lena", "Can I come after I finish the painting?"], ["Sam", "Of course! Come at eight. And don't bring a present!"]],
      qs: [
        { q: "Что Лена собирается делать на выходных?", a: ["Красить спальню", "Ремонтировать кухню", "Переезжать"], c: 0 },
        { q: "Кто ей поможет?", a: ["Её брат", "Сэм", "Никто"], c: 0 },
        { q: "Сколько гостей пригласит Сэм?", a: ["Десять", "Двадцать", "Пять"], c: 0 },
        { q: "Во сколько Лене прийти?", a: ["В восемь", "В семь", "В десять"], c: 0 }
      ]
    },
    speak: ["I'm going to learn Spanish next year.", "What are you going to do tomorrow?", "We aren't going to buy a car.", "Look at the sky! It's going to rain."],
    write: {
      trans: [
        ["Я собираюсь учить испанский.", ["I'm going to learn Spanish", "I am going to learn Spanish", "I'm going to study Spanish", "I am going to study Spanish"]],
        ["Что ты собираешься делать завтра?", ["What are you going to do tomorrow", "What are you going to do"]],
        ["Мы не собираемся переезжать.", ["We aren't going to move", "We are not going to move", "We're not going to move"]],
        ["Она собирается сдать экзамен.", ["She's going to pass the exam", "She is going to pass the exam", "She's going to pass an exam", "She is going to pass an exam", "She's going to pass her exam", "She is going to pass her exam", "She's going to take the exam", "She is going to take the exam", "She's going to take an exam", "She is going to take an exam", "She is going to take her exam"]]
      ],
      prompt: "Напиши о своих планах на следующий год: что ты собираешься сделать, изучить, купить или изменить, а чего делать не собираешься.",
      minWords: 60, use: ["going to", "next year", "not going to", "hope"],
      model: "Next year is going to be very busy for me. First, I'm going to start an English course, because I want to travel abroad. I hope I'm going to pass the exam in December. Second, my wife and I are going to repair our kitchen and paint the bedroom. We're not going to buy a new car, because it is too expensive. In the summer we're going to visit my parents and celebrate my father's birthday."
    }
  }
];
M.exam = {
  read: {
    title: "Письмо из Эдинбурга",
    text: "Hi Masha, how are you? I'm writing from Edinburgh. I'm here for two weeks with my sister. Yesterday we went shopping. The main street is the busiest place in the city, so we went to a small market near the castle. It was much cheaper than the big shops, and the things there were more interesting. I bought a wool scarf for you. It's grey, your favourite colour! I also tried on some boots, but they were too small, and the larger size was too expensive. Maybe next time. In the evening we had dinner in a Scottish restaurant. I'd like to say the food was delicious, but my fish was too salty! My sister's soup was better. Tomorrow we're going to visit the castle, and on Saturday we're going to take a train to the mountains. We're going to stay in a small hotel there for three nights. I'm going to send you lots of photos! Love, Kate",
    gloss: [["main street", "главная улица"], ["castle", "замок"], ["favourite", "любимый"], ["salty", "солёный"], ["lots of", "много"]],
    qs: [
      { q: "Где сейчас Кейт?", a: ["В Эдинбурге", "В Лондоне", "В горах"], c: 0 },
      { q: "Почему они пошли на маленький рынок?", a: ["На главной улице слишком много людей", "Там была распродажа", "Рынок рядом с отелем"], c: 0 },
      { q: "Что Кейт купила Маше?", a: ["Шерстяной шарф", "Ботинки", "Перчатки"], c: 0 },
      { q: "Что было не так с рыбой?", a: ["Слишком солёная", "Слишком острая", "Холодная"], c: 0 },
      { q: "Что они собираются делать в субботу?", a: ["Поехать на поезде в горы", "Посетить замок", "Ходить по магазинам"], c: 0 }
    ]
  },
  listen: {
    lines: [["Waiter", "Good evening. Have you booked a table?"], ["Tom", "Yes, a table for three. The name is Brown."], ["Waiter", "This way, please. Would you like anything to drink?"], ["Tom", "A bottle of sparkling water, please. Our friend is going to be late."], ["Mia", "Tom, this restaurant is more expensive than I thought."], ["Tom", "Yes, but it's the best place in town for fish. And it's Jack's birthday!"], ["Mia", "OK. What are you going to have?"], ["Tom", "I'd like the steak. The fish dishes are too big for me."], ["Mia", "I'm going to have the vegetarian pasta. Oh, look, here's Jack!"], ["Jack", "Sorry I'm late! The traffic was terrible."]],
    qs: [
      { q: "На сколько человек заказан столик?", a: ["На троих", "На двоих", "На четверых"], c: 0 },
      { q: "Что Том заказывает пить?", a: ["Бутылку газированной воды", "Сок", "Вино"], c: 0 },
      { q: "Почему они выбрали этот ресторан?", a: ["Там лучшая рыба в городе", "Он самый дешёвый", "Он рядом с домом"], c: 0 },
      { q: "Что будет есть Мия?", a: ["Вегетарианскую пасту", "Стейк", "Рыбу"], c: 0 },
      { q: "Почему Джек опоздал?", a: ["Были ужасные пробки", "Он забыл о встрече", "Он покупал подарок"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Эта куртка дороже, чем та.", ["This jacket is more expensive than that one", "This jacket is more expensive than that jacket", "This jacket is more expensive than that"]],
      ["Эти туфли слишком маленькие.", ["These shoes are too small"]],
      ["Я бы хотел чашку кофе.", ["I'd like a cup of coffee", "I would like a cup of coffee", "I'd like a cup of coffee please", "I would like a cup of coffee please"]],
      ["Мы собираемся пожениться летом.", ["We're going to get married in the summer", "We are going to get married in the summer", "We're going to get married in summer", "We are going to get married in summer", "We're going to get married this summer", "We are going to get married this summer"]],
      ["Это самый популярный ресторан в городе.", ["It's the most popular restaurant in the city", "This is the most popular restaurant in the city", "It's the most popular restaurant in town", "This is the most popular restaurant in town", "It's the most popular restaurant in the town", "This is the most popular restaurant in the town"]]
    ],
    prompt: "Напиши письмо другу о том, как ты провёл(а) субботу: где делал(а) покупки, что примерял(а) и купил(а), где ел(а). Расскажи, что ты собираешься делать в следующие выходные.",
    minWords: 80, use: ["cheaper", "too", "I'd like", "going to"],
    model: "Hi Anna! Last Saturday I went to the new shopping centre with my sister. It is bigger than the old one, and the shops are cheaper. I tried on a lot of clothes. The jeans I liked were too long, but I found a nice sweater and a leather belt. Then we had lunch in an Italian café. The pizza was delicious, but the coffee wasn't hot enough. Next weekend I'm going to visit my grandmother in the village. I'd like to bake a cake for her. Would you like to come with me? Love, Masha"
  },
  speak: ["The market is cheaper than the supermarket.", "These trousers are too long for me.", "I'd like a table for two, please.", "Would you like a dessert?", "I'm going to visit my parents next weekend."],
  grammar: [
    { q: "This shop is ___ than that one. (дороже)", a: ["more expensive", "expensiver", "most expensive"], c: 0 }, { q: "It's the ___ café in town. (лучшее)", a: ["best", "better", "goodest"], c: 0 },
    { q: "This coat isn't warm ___.", a: ["enough", "too", "very"], c: 0 }, { q: "___ you like some tea?", a: ["Would", "Do", "Are"], c: 0 },
    { q: "We're going ___ a new car.", a: ["to buy", "buy", "buying"], c: 0 }, { q: "The shoes are ___ small. I can't wear them.", a: ["too", "enough", "much"], c: 0 }
  ]
};
})();

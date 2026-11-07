// Месяц 6 (A2): Работа и здоровье. В конце — экзамен уровня A2 по материалу месяцев 4–6.
(function(){
const M = window.MD_PROGRAM.en.months[5];
M.weeks = [
  {
    t: "Профессии и резюме",
    words: [
      ["CV", "резюме", "си-вИ"], ["experience", "опыт", "икспИэриэнс"], ["skill", "навык", "скил"], ["degree", "диплом, учёная степень", "дигрИ"], ["university", "университет", "юнивЁсити"],
      ["lawyer", "юрист", "лОйэ"], ["accountant", "бухгалтер", "экАунтэнт"], ["designer", "дизайнер", "дизАйнэ"], ["architect", "архитектор", "Акитэкт"], ["pilot", "пилот", "пАйлэт"],
      ["police officer", "полицейский", "пэлИс Офисэ"], ["scientist", "учёный", "сАйэнтист"], ["mechanic", "механик", "микЭник"], ["farmer", "фермер", "фАмэ"], ["hairdresser", "парикмахер", "хЭэдрэсэ"],
      ["salary", "зарплата", "сЭлэри"], ["interview", "собеседование, интервью", "Интэвью"], ["apply", "подавать заявление", "эплАй"], ["employer", "работодатель", "имплОйэ"], ["full-time", "на полный рабочий день", "фул-тайм"],
      ["part-time", "на неполный рабочий день", "пат-тайм"], ["career", "карьера", "кэрИэ"], ["ever", "когда-нибудь", "Эвэ"], ["been", "был (3-я форма от be)", "бин"], ["foreign language", "иностранный язык", "фОрин лЭнгуидж"],
      ["experienced", "опытный", "икспИэриэнст"], ["responsible", "ответственный", "риспОнсэбл"], ["well-paid", "хорошо оплачиваемый", "уэл-пэйд"], ["creative", "творческий", "криЭйтив"], ["team", "команда", "тим"]
    ],
    phrases: [["What do you do?", "Кем ты работаешь?"], ["I'm looking for a job.", "Я ищу работу."], ["I have five years of experience.", "У меня пять лет опыта."], ["Have you ever worked in a team?", "Ты когда-нибудь работал в команде?"], ["When can you start?", "Когда вы можете начать?"], ["I'd like to apply for this job.", "Я бы хотел откликнуться на эту вакансию."]],
    grammar: {
      title: "Present Perfect: ever / never",
      text: "Present Perfect рассказывает об опыте: что человек делал (или не делал) в жизни до сих пор, без точного времени. Форма: have / has + третья форма глагола (V3): I have worked, she has been. У правильных глаголов V3 = глагол + -ed (work → worked), у неправильных её нужно учить: be → been, do → done, see → seen, write → written. Ever («когда-нибудь») ставим в вопросах: Have you ever worked abroad? Never («никогда») — в утвердительном предложении, без not: I have never been to London. Краткие ответы: Yes, I have. / No, I haven't. Если называем точное время (last year, in 2020), нужен Past Simple: I worked in a bank in 2020.",
      examples: [["Have you ever worked in a team?", "Ты когда-нибудь работал в команде?"], ["I've never written a CV.", "Я никогда не писал резюме."], ["She has worked as a designer.", "Она работала дизайнером."], ["He's never had a full-time job.", "У него никогда не было работы на полный день."], ["Have you ever been to London? Yes, I have.", "Ты когда-нибудь был в Лондоне? Да, был."]],
      quiz: [
        { q: "Have you ___ worked abroad?", a: ["ever", "never", "yet"], c: 0 }, { q: "I have ___ been to an interview. (никогда)", a: ["never", "ever", "not"], c: 0 },
        { q: "She ___ worked as a lawyer.", a: ["has", "have", "is"], c: 0 }, { q: "Have you ever ___ a CV?", a: ["written", "wrote", "write"], c: 0 },
        { q: "Have they ever been to Paris? No, they ___.", a: ["haven't", "didn't", "aren't"], c: 0 }, { q: "He has ___ in three different companies.", a: ["worked", "work", "working"], c: 0 },
        { q: "I ___ in a bank in 2019.", a: ["worked", "have worked", "have work"], c: 0 }, { q: "We've never ___ a real pilot.", a: ["met", "meet", "meeted"], c: 0 }
      ]
    },
    read: {
      title: "Письмо работодателю",
      text: "Dear Sir or Madam, I am writing to apply for the job of designer at your company. I saw your advertisement online last week. My name is Anna Smirnova and I am twenty-eight. I have a degree in design from Moscow University. I have worked as a designer for five years, first in a small magazine and then in a big advertising company. I have designed websites, books and posters. I have never worked abroad, but I have travelled a lot and I speak two foreign languages: English and German. I am creative and responsible. I like working in a team, but I can also work alone. I have never missed a deadline! At the moment I am working part-time, and I am looking for a full-time job in a bigger team. I attach my CV. I am free for an interview any day next week. Yours faithfully, Anna Smirnova",
      gloss: [["advertisement", "объявление"], ["advertising company", "рекламная компания"], ["designed", "разрабатывала"], ["posters", "плакаты"], ["alone", "одна, самостоятельно"], ["deadline", "срок сдачи"], ["attach", "прилагаю"], ["Yours faithfully", "С уважением"]],
      qs: [
        { q: "На какую работу претендует Анна?", a: ["Дизайнера", "Журналиста", "Переводчика"], c: 0 },
        { q: "Сколько лет она работает дизайнером?", a: ["Пять", "Восемь", "Два"], c: 0 },
        { q: "Работала ли она за границей?", a: ["Нет, никогда", "Да, в Германии", "Да, пять лет"], c: 0 },
        { q: "Какую работу она ищет?", a: ["На полный день", "На неполный день", "Удалённую"], c: 0 }
      ]
    },
    listen: {
      lines: [["Manager", "Please sit down. So, Mr Petrov, have you ever worked in a hotel?"], ["Oleg", "Yes, I have. I worked as a receptionist in Sochi for two years."], ["Manager", "Good. Have you ever worked at night?"], ["Oleg", "No, I've never worked at night, but I don't mind."], ["Manager", "What foreign languages do you speak?"], ["Oleg", "English and a little Turkish."], ["Manager", "Have you ever had problems with guests?"], ["Oleg", "Sometimes, but I'm calm and I always try to help."], ["Manager", "Excellent. The job is full-time and the salary is two thousand a month. When can you start?"], ["Oleg", "Next Monday."]],
      qs: [
        { q: "Кем Олег работал в Сочи?", a: ["Администратором", "Официантом", "Поваром"], c: 0 },
        { q: "Работал ли он ночью?", a: ["Нет, никогда", "Да, два года", "Да, иногда"], c: 0 },
        { q: "Какие языки он знает?", a: ["Английский и немного турецкий", "Только английский", "Немецкий и английский"], c: 0 },
        { q: "Когда он может начать работу?", a: ["В следующий понедельник", "Завтра", "Через месяц"], c: 0 }
      ]
    },
    speak: ["Have you ever worked abroad?", "I've never written a CV.", "I have a degree in economics.", "I'm creative and responsible."],
    write: {
      trans: [
        ["Ты когда-нибудь работал за границей?", ["Have you ever worked abroad"]],
        ["Я никогда не писал резюме.", ["I have never written a CV", "I've never written a CV", "I have never written a resume", "I've never written a resume", "I never wrote a CV"]],
        ["Она работала дизайнером.", ["She has worked as a designer", "She worked as a designer", "She's worked as a designer", "She was a designer"]],
        ["Я ищу работу.", ["I'm looking for a job", "I am looking for a job", "I'm looking for work", "I am looking for work"]]
      ],
      prompt: "Напиши короткое письмо работодателю о себе: какое у тебя образование, где ты работал(а), что ты уже умеешь и чего никогда не делал(а).",
      minWords: 60, use: ["have worked", "never", "experience", "skills"],
      model: "Dear Sir or Madam, I would like to apply for the job of manager in your shop. I have a degree in economics from Kazan University. I have worked in sales for six years, and I have a lot of experience with customers. My skills include English, computers and team work. I have never worked in a big company, but I learn fast and I am responsible and creative. I am free for an interview next week. Yours faithfully, Ilya Orlov"
    }
  },
  {
    t: "У врача",
    words: [
      ["appointment", "запись (к врачу), встреча", "эпОйнтмэнт"], ["clinic", "поликлиника, клиника", "клИник"], ["headache", "головная боль", "хЭдэйк"], ["toothache", "зубная боль", "тУсэйк"], ["stomach ache", "боль в животе", "стАмэк эйк"],
      ["sore throat", "боль в горле", "сор сроут"], ["cough", "кашель; кашлять", "коф"], ["flu", "грипп", "флу"], ["temperature", "температура", "тЭмпрэчэ"], ["pain", "боль", "пэйн"],
      ["hurt", "болеть, причинять боль", "хёрт"], ["medicine", "лекарство", "мЭдсин"], ["pill", "таблетка", "пил"], ["prescription", "рецепт (от врача)", "прискрИпшн"], ["dentist", "стоматолог", "дЭнтист"],
      ["healthy", "здоровый", "хЭлси"], ["sick", "больной; тошнит", "сик"], ["feel", "чувствовать (себя)", "фил"], ["get better", "поправляться", "гет бЭтэ"], ["rest", "отдыхать; отдых", "рэст"],
      ["head", "голова", "хэд"], ["back", "спина", "бэк"], ["arm", "рука (от плеча до кисти)", "ам"], ["leg", "нога", "лэг"], ["stomach", "живот, желудок", "стАмэк"],
      ["tooth", "зуб", "тус"], ["already", "уже", "олрЭди"], ["yet", "уже (в вопросе), ещё (не)", "йет"], ["just", "только что", "джаст"], ["allergic", "аллергический; с аллергией", "элЁджик"]
    ],
    phrases: [["I'd like to make an appointment.", "Я бы хотел записаться на приём."], ["What's the matter?", "Что вас беспокоит?"], ["I've got a sore throat.", "У меня болит горло."], ["My leg hurts.", "У меня болит нога."], ["Take one pill three times a day.", "Принимайте по одной таблетке три раза в день."], ["Get well soon!", "Выздоравливай!"]],
    grammar: {
      title: "already / yet / just",
      text: "Already, yet и just часто используются с Present Perfect. Just — «только что», ставится между have и V3: I've just seen the doctor. Already — «уже» (раньше, чем ожидали), тоже ставится между have и V3: She has already taken the medicine. Yet в вопросах значит «уже?», в отрицаниях — «ещё не», и ставится в конце предложения: Have you made an appointment yet? I haven't taken the pills yet. Сравни: Has he left yet? — обычный вопрос «Он уже ушёл?», а Has he already left? — удивление «Как, он уже ушёл?»",
      examples: [["I've just made an appointment.", "Я только что записался на приём."], ["Have you taken your medicine yet?", "Ты уже принял лекарство?"], ["She hasn't seen the doctor yet.", "Она ещё не была у врача."], ["My headache has already gone.", "Моя головная боль уже прошла."], ["The dentist has just called.", "Только что звонил стоматолог."]],
      quiz: [
        { q: "I haven't seen the doctor ___.", a: ["yet", "already", "just"], c: 0 }, { q: "I've ___ taken a pill. (только что)", a: ["just", "yet", "ever"], c: 0 },
        { q: "She has ___ made an appointment. (уже)", a: ["already", "yet", "ever"], c: 0 }, { q: "He hasn't ___ to the dentist yet.", a: ["been", "was", "be"], c: 0 },
        { q: "My back has ___ stopped hurting. (только что)", a: ["just", "yet", "ever"], c: 0 }, { q: "I've just ___ the doctor.", a: ["seen", "saw", "see"], c: 0 },
        { q: "Have you finished your pills? No, not ___.", a: ["yet", "already", "just"], c: 0 }, { q: "The nurse ___ just called you.", a: ["has", "have", "is"], c: 0 }
      ]
    },
    read: {
      title: "Сообщение от мамы",
      text: "Hi Dima, how are you feeling today? Your dad told me you've got a bad cold. Have you seen a doctor yet? Please don't wait. I know you're busy at work, but your health is more important. I've just called our family doctor, Dr Wilson. She says it's probably flu, because a lot of people in town have got it. She has already made an appointment for you for tomorrow at ten. Don't be late! Remember: drink a lot of hot tea with honey and lemon and stay in bed. Have you got any medicine for your sore throat? If not, don't worry. I've already bought some pills for you. Your dad is going to bring them this evening. And please take your temperature twice a day. If it's higher than thirty-nine, call me immediately. I hope you'll get better soon! Love, Mum. P.S. Have you eaten anything yet? I've just made some chicken soup!",
      gloss: [["health", "здоровье"], ["honey", "мёд"], ["lemon", "лимон"], ["stay in bed", "лежать в постели"], ["take your temperature", "измерять температуру"], ["immediately", "немедленно"]],
      qs: [
        { q: "Чем, по мнению врача, болен Дима?", a: ["Скорее всего, гриппом", "Простудой", "Аллергией"], c: 0 },
        { q: "Когда у Димы приём у врача?", a: ["Завтра в 10", "Сегодня вечером", "Послезавтра"], c: 0 },
        { q: "Кто привезёт таблетки?", a: ["Папа", "Мама", "Врач"], c: 0 },
        { q: "Что мама только что приготовила?", a: ["Куриный суп", "Чай с мёдом", "Пирог"], c: 0 }
      ]
    },
    listen: {
      lines: [["Doctor", "Good morning, Mrs Brown. What's the problem?"], ["Mrs Brown", "I've had a terrible headache for three days, and now my back hurts too."], ["Doctor", "Have you taken any medicine yet?"], ["Mrs Brown", "Yes, I've already tried some pills from the pharmacy, but they didn't help."], ["Doctor", "Have you got a temperature?"], ["Mrs Brown", "No, I've just checked it. It's normal."], ["Doctor", "Do you work at a computer?"], ["Mrs Brown", "Yes, about ten hours a day."], ["Doctor", "That's probably the reason. Here's a prescription. Take one pill twice a day and have a rest from the screen."], ["Mrs Brown", "Thank you, doctor."]],
      qs: [
        { q: "Что беспокоит миссис Браун?", a: ["Головная боль и спина", "Горло и кашель", "Живот"], c: 0 },
        { q: "Помогли ли ей таблетки из аптеки?", a: ["Нет", "Да, немного", "Она их не пробовала"], c: 0 },
        { q: "Какая у неё температура?", a: ["Нормальная", "Высокая", "Она не измеряла"], c: 0 },
        { q: "В чём, по мнению врача, причина?", a: ["В работе за компьютером", "В гриппе", "В аллергии"], c: 0 }
      ]
    },
    speak: ["I've got a terrible headache.", "Have you taken your medicine yet?", "I've just made an appointment.", "My back hurts."],
    write: {
      trans: [
        ["Я только что был у врача.", ["I've just been to the doctor", "I have just been to the doctor", "I've just seen the doctor", "I have just seen the doctor", "I've just seen a doctor", "I have just seen a doctor", "I've just been to the doctor's", "I have just been to the doctor's", "I've just been to a doctor", "I have just been to a doctor"]],
        ["Ты уже принял лекарство?", ["Have you taken your medicine yet", "Have you taken the medicine yet", "Have you already taken your medicine", "Have you already taken the medicine", "Have you taken your medicine already", "Have you taken the medicine already", "Did you take your medicine", "Did you take the medicine"]],
        ["У меня болит голова.", ["I have a headache", "I've got a headache", "I have got a headache", "My head hurts", "My head aches"]],
        ["Она ещё не записалась к врачу.", ["She hasn't made an appointment yet", "She has not made an appointment yet", "She hasn't made an appointment with the doctor yet", "She has not made an appointment with the doctor yet", "She hasn't made a doctor's appointment yet", "She has not made a doctor's appointment yet"]]
      ],
      prompt: "Напиши сообщение другу о том, что ты заболел(а): что у тебя болит, что ты уже сделал(а), а что ещё нет. Используй already, yet и just.",
      minWords: 55, use: ["already", "yet", "just", "doctor"],
      model: "Hi Lena! Sorry, I can't come to the cinema tonight. I've got a bad cold. I have a sore throat and a headache, and my temperature is thirty-eight. I've already taken some pills and I've just made tea with honey. I haven't seen a doctor yet, but I've made an appointment for tomorrow morning. I hope I'll get better soon. Let's go to the cinema next week!"
    }
  },
  {
    t: "Опыт",
    words: [
      ["try", "пробовать", "трай"], ["skiing", "катание на лыжах", "скИинг"], ["diving", "дайвинг, ныряние", "дАйвинг"], ["climb", "подниматься, взбираться", "клайм"], ["win", "выигрывать, побеждать", "уин"],
      ["prize", "приз", "прайз"], ["competition", "соревнование, конкурс", "компэтИшн"], ["surf", "заниматься сёрфингом", "сёрф"], ["famous", "знаменитый", "фЭймэс"], ["ride a horse", "ездить верхом", "райд э хорс"],
      ["snake", "змея", "снэйк"], ["jump", "прыгать", "джамп"], ["frightening", "страшный, пугающий", "фрАйтнинг"], ["roller coaster", "американские горки", "рОулэ кОустэ"], ["exciting", "захватывающий", "иксАйтинг"],
      ["dangerous", "опасный", "дЭйнджэрэс"], ["once", "один раз; однажды", "уанс"], ["twice", "дважды", "туайс"], ["several times", "несколько раз", "сЭврэл таймз"], ["theme park", "парк развлечений", "сим пак"],
      ["should", "следует, стоит", "шуд"], ["recommend", "рекомендовать", "рэкэмЭнд"], ["worth", "стоящий (It's worth it — оно того стоит)", "уёс"], ["festival", "фестиваль", "фЭстивл"], ["piano", "пианино", "пиЭноу"],
      ["marathon", "марафон", "мЭрэсэн"], ["hot-air balloon", "воздушный шар", "хот-Эа бэлУн"], ["cave", "пещера", "кэйв"], ["wild", "дикий", "уайлд"], ["nervous", "нервничающий", "нЁвэс"]
    ],
    phrases: [["Have you ever tried it?", "Ты когда-нибудь пробовал это?"], ["It was the best day of my life.", "Это был лучший день в моей жизни."], ["You should try it!", "Тебе стоит попробовать!"], ["It's worth it.", "Оно того стоит."], ["I was really nervous.", "Я очень нервничал."], ["What should I do?", "Что мне делать?"]],
    grammar: {
      title: "should / shouldn't",
      text: "Should + глагол без to — так даём совет или говорим, что, по нашему мнению, правильно: You should try diving. Shouldn't (= should not) — совет этого не делать: You shouldn't swim here, it's dangerous. Should одинаков для всех лиц и не получает -s: She should rest. Вопрос: Should I go? What should I do? Мягче звучит с I think: I think you should see a doctor. Отрицательный совет по-английски обычно строят так: I don't think you should go alone. Совет часто опирается на собственный опыт: I've been there. You should go!",
      examples: [["You should try skiing. It's great fun.", "Тебе стоит попробовать покататься на лыжах. Это очень весело."], ["You shouldn't climb alone.", "Тебе не стоит лазить по горам одному."], ["Should I take a warm jacket?", "Мне взять тёплую куртку?"], ["I think you should enter the competition.", "Думаю, тебе стоит участвовать в конкурсе."], ["I've been there. You should go!", "Я там был. Тебе стоит поехать!"]],
      quiz: [
        { q: "You ___ try diving. It's amazing!", a: ["should", "shoulds", "should to"], c: 0 }, { q: "You ___ swim in the river. It's dangerous.", a: ["shouldn't", "should", "don't should"], c: 0 },
        { q: "She should ___ a rest.", a: ["have", "has", "to have"], c: 0 }, { q: "___ I take a warm jacket?", a: ["Should", "Do", "Am"], c: 0 },
        { q: "I don't think you ___ go alone.", a: ["should", "shouldn't", "should to"], c: 0 }, { q: "What should I ___?", a: ["do", "to do", "doing"], c: 0 },
        { q: "Have you ever ___ skiing? You should try it!", a: ["been", "went", "go"], c: 0 }, { q: "He ___ eat so much fast food. It's bad for him.", a: ["shouldn't", "should", "doesn't should"], c: 0 }
      ]
    },
    read: {
      title: "Попробуй что-то новое!",
      text: "I'm forty-five, and two years ago I made a decision: every year I'm going to try something new. Here are some of my experiences. Last winter I went skiing for the first time in my life. I was nervous and I fell about twenty times, but on the last day I skied down a hill without falling! Then in the summer I went diving in Egypt. I saw colourful fish and even a small shark. It was the most exciting day of my life. This year I've run my first marathon. I didn't win a prize, of course, but I finished it, and my family was very proud of me. I've also helped at a music festival. I've never worked so hard, but it was great fun. What's my advice? You shouldn't be afraid of new things. You should start with something small, for example a cooking class. And you shouldn't think, 'I'm too old.' I've met people of seventy at the ski school!",
      gloss: [["decision", "решение"], ["fell", "упал, падал"], ["without falling", "ни разу не упав"], ["colourful", "разноцветный"], ["shark", "акула"], ["proud of", "гордый (кем-то)"], ["cooking class", "кулинарный курс"]],
      qs: [
        { q: "Сколько лет автору?", a: ["45", "70", "25"], c: 0 },
        { q: "Где автор занимался дайвингом?", a: ["В Египте", "В Турции", "В Таиланде"], c: 0 },
        { q: "Выиграл ли автор приз на марафоне?", a: ["Нет, но добежал до конца", "Да, занял первое место", "Он не закончил марафон"], c: 0 },
        { q: "Какой совет даёт автор?", a: ["Не бояться нового и начинать с малого", "Сразу пробовать опасные вещи", "Делать всё только с друзьями"], c: 0 }
      ]
    },
    listen: {
      lines: [["Mike", "Have you ever been up in a hot-air balloon?"], ["Sara", "No, never. Have you?"], ["Mike", "Yes, last year in Turkey. It was amazing. You should try it!"], ["Sara", "I don't know. I'm afraid of heights."], ["Mike", "It's not dangerous, really. And the view is wonderful."], ["Sara", "Is it expensive?"], ["Mike", "About a hundred and fifty euros. It's worth it. But you should book early."], ["Sara", "OK. Should I take warm clothes?"], ["Mike", "Yes, you should. It's cold early in the morning."]],
      qs: [
        { q: "Где Майк летал на воздушном шаре?", a: ["В Турции", "В Египте", "Во Франции"], c: 0 },
        { q: "Чего боится Сара?", a: ["Высоты", "Воды", "Самолётов"], c: 0 },
        { q: "Сколько стоит полёт?", a: ["Около 150 евро", "Около 50 евро", "Около 500 евро"], c: 0 },
        { q: "Что советует взять Майк?", a: ["Тёплую одежду", "Фотоаппарат", "Еду"], c: 0 }
      ]
    },
    speak: ["You should try diving.", "You shouldn't swim here.", "Have you ever climbed a mountain?", "What should I do?"],
    write: {
      trans: [
        ["Тебе стоит попробовать дайвинг.", ["You should try diving", "You should try scuba diving", "You should go diving"]],
        ["Тебе не следует плавать здесь.", ["You shouldn't swim here", "You should not swim here"]],
        ["Мне взять тёплую куртку?", ["Should I take a warm jacket", "Shall I take a warm jacket", "Should I take a warm coat", "Shall I take a warm coat", "Should I bring a warm jacket", "Shall I bring a warm jacket"]],
        ["Я никогда не катался на лыжах.", ["I have never skied", "I've never skied", "I have never been skiing", "I've never been skiing", "I have never gone skiing", "I've never gone skiing", "I never skied"]]
      ],
      prompt: "Расскажи о самом интересном или необычном опыте в своей жизни. Посоветуй другу, стоит ли ему это попробовать и что нужно (или не нужно) делать.",
      minWords: 65, use: ["have ever", "never", "should", "shouldn't"],
      model: "The most exciting thing I have ever done was a trip to Altai with my friends. We climbed a mountain and slept in tents near a wild lake. It was cold, but the stars were amazing. I have never seen so many stars! I think you should try it too. You should take warm clothes and good boots. You shouldn't go alone, and you shouldn't climb without a guide, because it can be dangerous."
    }
  },
  {
    t: "Советы",
    words: [
      ["advice", "совет", "эдвАйс"], ["advise", "советовать", "эдвАйз"], ["if", "если", "иф"], ["stress", "стресс", "стрэс"], ["relax", "расслабляться", "рилЭкс"],
      ["exercise", "физические упражнения; заниматься спортом", "Эксэсайз"], ["diet", "питание, диета", "дАйэт"], ["habit", "привычка", "хЭбит"], ["smoke", "курить", "смоук"], ["fast food", "фастфуд", "фаст фуд"],
      ["screen", "экран", "скрин"], ["break", "перерыв", "брэйк"], ["fresh air", "свежий воздух", "фрэш эа"], ["energy", "энергия, силы", "Энэджи"], ["weight", "вес", "уэйт"],
      ["keep fit", "поддерживать форму", "кип фит"], ["probably", "вероятно, наверное", "прОбэбли"], ["solve", "решать (проблему)", "солв"], ["calm", "спокойный", "кам"], ["lonely", "одинокий", "лОунли"],
      ["mood", "настроение", "муд"], ["upset", "расстроенный", "апсЭт"], ["afraid", "испуганный (be afraid — бояться)", "эфрЭйд"], ["worry", "беспокоиться", "уАри"], ["mistake", "ошибка", "мистЭйк"],
      ["chance", "шанс, возможность", "чанс"], ["regularly", "регулярно", "рЭгьюлэли"], ["instead", "вместо этого", "инстЭд"], ["routine", "распорядок дня", "рутИн"], ["vitamins", "витамины", "вИтэминз"]
    ],
    phrases: [["What's your advice?", "Что ты посоветуешь?"], ["Can I give you some advice?", "Можно дать тебе совет?"], ["Why don't you take a break?", "Почему бы тебе не сделать перерыв?"], ["Don't worry about it.", "Не переживай из-за этого."], ["Try to relax.", "Постарайся расслабиться."], ["Take care of yourself!", "Береги себя!"]],
    grammar: {
      title: "First Conditional",
      text: "First Conditional — реальное условие в будущем: если что-то случится, будет результат. Схема: If + Present Simple, will + глагол: If you go to bed early, you will feel better. Важно: после if не ставим will, даже если по-русски будущее время: If it rains, we'll stay at home (а не If it will rain). Части можно поменять местами, тогда запятая не нужна: You'll feel better if you sleep more. Вместо will в главной части может быть повелительное наклонение: If you feel stressed, take a break. Отрицание: If you don't eat breakfast, you won't have enough energy.",
      examples: [["If you sleep more, you'll feel better.", "Если будешь больше спать, почувствуешь себя лучше."], ["If it rains, we'll stay at home.", "Если пойдёт дождь, мы останемся дома."], ["You won't lose weight if you eat fast food.", "Ты не похудеешь, если будешь есть фастфуд."], ["If you feel stressed, take a break.", "Если чувствуешь стресс, сделай перерыв."], ["What will you do if you don't pass?", "Что ты будешь делать, если не сдашь?"]],
      quiz: [
        { q: "If you ___ more, you'll feel better.", a: ["sleep", "will sleep", "slept"], c: 0 }, { q: "If it rains, we ___ at home.", a: ["will stay", "stayed", "staying"], c: 0 },
        { q: "You won't have energy if you ___ eat breakfast.", a: ["don't", "won't", "didn't"], c: 0 }, { q: "If she exercises regularly, she ___ fit.", a: ["will keep", "kept", "keeping"], c: 0 },
        { q: "___ you feel stressed, take a break.", a: ["If", "Will", "Unless"], c: 0 }, { q: "What will you do if you ___ the exam?", a: ["fail", "will fail", "failed"], c: 0 },
        { q: "If you don't stop smoking, you ___ healthy.", a: ["won't be", "aren't", "don't be"], c: 0 }, { q: "If I ___ time tomorrow, I'll call you.", a: ["have", "will have", "had"], c: 0 }
      ]
    },
    read: {
      title: "Спросите доктора Кейт",
      text: "Dear Dr Kate, I'm thirty-two and I work in an office. I'm always tired, I often feel stressed and I've put on a lot of weight this year. I sit at a computer all day and in the evening I look at my phone until midnight. What should I do? Max. Dear Max, don't worry, you can change this! Here is my advice. First, sleep more. If you stop using your phone an hour before bed, you'll sleep better. Second, move more. You don't have to go to the gym. If you walk to work or take the stairs, you'll have more energy. Third, look at your diet. If you eat less fast food and more fruit and vegetables, you'll lose weight slowly but safely. Also, take a break every hour. If you sit for too long, your back will hurt. And don't forget to see your friends. If you're lonely, you'll feel worse. Change one habit at a time. If you try to change everything at once, you'll probably give up. Good luck! Kate",
      gloss: [["put on weight", "набрать вес"], ["until midnight", "до полуночи"], ["slowly", "медленно"], ["safely", "безопасно"], ["at a time", "за один раз"], ["at once", "сразу"]],
      qs: [
        { q: "Какие проблемы у Макса?", a: ["Усталость, стресс и лишний вес", "Боль в спине и кашель", "Проблемы с начальником"], c: 0 },
        { q: "Что Кейт советует для хорошего сна?", a: ["Не пользоваться телефоном за час до сна", "Пить чай на ночь", "Ложиться в девять"], c: 0 },
        { q: "Нужно ли Максу ходить в спортзал?", a: ["Нет, достаточно ходить пешком и по лестнице", "Да, каждый день", "Да, три раза в неделю"], c: 0 },
        { q: "Почему не стоит менять всё сразу?", a: ["Скорее всего, бросишь", "Это опасно для здоровья", "Это слишком дорого"], c: 0 }
      ]
    },
    listen: {
      lines: [["Tom", "I've got an important exam next week and I'm really worried."], ["Lisa", "Have you started studying yet?"], ["Tom", "Yes, but I study until two in the morning and I'm always tired."], ["Lisa", "That's a mistake. If you don't sleep, you won't remember anything."], ["Tom", "But if I sleep more, I won't have enough time!"], ["Lisa", "Make a plan. If you study for two hours every morning, you'll be fine."], ["Tom", "Maybe you're right. What about coffee? I drink five cups a day."], ["Lisa", "That's too much. If you drink less coffee, you'll feel calmer."], ["Tom", "OK, I'll try. Thanks, Lisa!"]],
      qs: [
        { q: "Почему Том волнуется?", a: ["У него важный экзамен", "Он потерял работу", "Он заболел"], c: 0 },
        { q: "До скольки Том занимается?", a: ["До двух часов ночи", "До полуночи", "До десяти вечера"], c: 0 },
        { q: "Что советует Лиза?", a: ["Составить план и заниматься по утрам", "Заниматься всю ночь", "Совсем не готовиться"], c: 0 },
        { q: "Сколько кофе пьёт Том?", a: ["Пять чашек в день", "Две чашки в день", "Он не пьёт кофе"], c: 0 }
      ]
    },
    speak: ["If you sleep more, you'll feel better.", "If it rains, we'll stay at home.", "You should take a break.", "What will you do if you miss the bus?"],
    write: {
      trans: [
        ["Если пойдёт дождь, мы останемся дома.", ["If it rains, we'll stay at home", "If it rains, we will stay at home", "We'll stay at home if it rains", "We will stay at home if it rains", "If it rains, we'll stay home", "If it rains, we will stay home", "We'll stay home if it rains", "We will stay home if it rains"]],
        ["Если будешь больше спать, почувствуешь себя лучше.", ["If you sleep more, you'll feel better", "If you sleep more, you will feel better", "You'll feel better if you sleep more", "You will feel better if you sleep more"]],
        ["Не волнуйся.", ["Don't worry", "Do not worry"]],
        ["Тебе стоит сделать перерыв.", ["You should take a break", "You should have a break"]]
      ],
      prompt: "Друг пишет тебе, что постоянно устаёт и плохо спит. Дай ему советы и объясни, что будет, если он им последует (If you…, you'll…).",
      minWords: 70, use: ["if", "will", "should", "habit"],
      model: "Hi Pavel! I'm sorry you feel tired all the time. Here is my advice. First, you should go to bed before eleven. If you sleep eight hours, you will have more energy. Second, you shouldn't drink coffee in the evening. Third, try to walk for thirty minutes every day. If you exercise regularly, you'll feel calmer and happier. Don't use your phone in bed. It's a bad habit! If you change these things, I'm sure you will feel better soon. Take care!"
    }
  }
];
// Экзамен уровня A2: тексты и грамматика по материалу месяцев 4–6
M.exam = {
  read: {
    title: "Новое начало",
    text: "Marina is thirty-four and she lives in Samara. For ten years she worked as an accountant in a big bank. The salary was good, but the job was boring and she was always stressed. 'I didn't like my life,' she says. 'I had headaches every week and I never had time for my family.' Last year she decided to change everything. She took a cooking course and now she works as a chef in a small vegetarian café. She earns less than before, but she is much happier. 'I've never felt so healthy,' she says. 'I've already lost five kilos, because I walk to work and I don't eat fast food any more.' In the summer Marina travelled to Italy to learn more about Italian food. While she was visiting a market in Bologna, she met a famous chef. He invited her to his restaurant, and she worked in his kitchen for a week. It was a wonderful experience. Now she has a new plan: she's going to open her own café next year. 'If I find a good place, I'll open it in the spring,' she says. 'My advice? You should do what you love!'",
    gloss: [["decided", "решила"], ["earns less", "зарабатывает меньше"], ["kilos", "килограммы"], ["any more", "больше не"], ["her own", "собственный"]],
    qs: [
      { q: "Почему Марине не нравилась работа в банке?", a: ["Работа была скучной, и было много стресса", "Была маленькая зарплата", "Банк был далеко от дома"], c: 0 },
      { q: "Кем Марина работает сейчас?", a: ["Поваром в вегетарианском кафе", "Бухгалтером", "Официанткой"], c: 0 },
      { q: "Почему она похудела?", a: ["Ходит на работу пешком и не ест фастфуд", "Сидит на строгой диете", "Ходит в спортзал"], c: 0 },
      { q: "Что случилось в Болонье?", a: ["Она познакомилась с известным поваром", "Она потеряла кошелёк", "Она открыла кафе"], c: 0 },
      { q: "Когда Марина хочет открыть кафе?", a: ["Весной следующего года, если найдёт место", "Этим летом", "Через пять лет"], c: 0 }
    ]
  },
  listen: {
    lines: [["Receptionist", "Good evening. Can I help you?"], ["Paul", "Yes, I'm in room 215. My wife isn't feeling well. She's got a high temperature."], ["Receptionist", "Oh, I'm sorry. Has she taken any medicine yet?"], ["Paul", "No, we didn't bring any medicine with us."], ["Receptionist", "There's a pharmacy opposite the hotel, but it has already closed. I'll call a doctor for you."], ["Paul", "Thank you. Will we have to pay?"], ["Receptionist", "Have you got travel insurance? If you have, you won't have to pay."], ["Paul", "Yes, we have. When will the doctor come?"], ["Receptionist", "In about thirty minutes. Your wife should drink a lot of water until then."], ["Paul", "OK. Thank you very much for your help."]],
    qs: [
      { q: "В каком номере живёт Пол?", a: ["215", "512", "250"], c: 0 },
      { q: "Что случилось с женой Пола?", a: ["У неё высокая температура", "Она сломала ногу", "Она потеряла паспорт"], c: 0 },
      { q: "Почему нельзя сходить в аптеку?", a: ["Она уже закрылась", "Она очень далеко", "Там нет нужного лекарства"], c: 0 },
      { q: "Почему, скорее всего, не придётся платить врачу?", a: ["У них есть страховка", "Врач работает в отеле", "Врач бесплатный для всех"], c: 0 },
      { q: "Что жене нужно делать, пока она ждёт врача?", a: ["Пить много воды", "Спать", "Ничего не есть"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Ты когда-нибудь был в Лондоне?", ["Have you ever been to London"]],
      ["Я только что купил билеты.", ["I've just bought the tickets", "I have just bought the tickets", "I've just bought tickets", "I have just bought tickets", "I just bought the tickets", "I just bought tickets"]],
      ["Тебе следует пойти к врачу.", ["You should go to the doctor", "You should see a doctor", "You should go to a doctor", "You should see the doctor", "You should go to the doctor's", "You should go and see a doctor"]],
      ["Если будет солнечно, мы пойдём в парк.", ["If it's sunny, we'll go to the park", "If it is sunny, we will go to the park", "If it's sunny, we will go to the park", "If it is sunny, we'll go to the park", "We'll go to the park if it's sunny", "We will go to the park if it is sunny", "We'll go to the park if it is sunny", "We will go to the park if it's sunny"]],
      ["Эта гостиница дешевле, чем та.", ["This hotel is cheaper than that one", "This hotel is cheaper than that hotel", "This hotel is cheaper than that"]]
    ],
    prompt: "Напиши письмо другу, с которым давно не общался(-ась): что нового на работе и со здоровьем, куда ты ездил(а) и что там случилось, какие у тебя планы. Дай другу совет.",
    minWords: 80, use: ["have never", "was", "going to", "should"],
    model: "Hi Kate! How are you? I'm sorry I haven't written for a long time. I've had a very busy year. In March I started a new job in a travel company. The salary is better than before, and I have already been to three countries for work. In June I went to Spain. While I was walking in Madrid, somebody stole my wallet, and I had to go to the police. But the trip was still wonderful. I have never eaten such good food! Next month I'm going to take a holiday and visit my parents. You should come and see me in the autumn. If you come, I'll show you the city! Love, Olya"
  },
  speak: ["Have you ever worked abroad?", "I've just made an appointment with the doctor.", "You should drink more water.", "If it rains, we'll take a taxi.", "This hotel is more comfortable than the last one."],
  grammar: [
    { q: "Have you ___ been to Spain?", a: ["ever", "never", "yet"], c: 0 }, { q: "I haven't finished my work ___.", a: ["yet", "already", "just"], c: 0 },
    { q: "You look tired. You ___ go to bed.", a: ["should", "shouldn't", "should to"], c: 0 }, { q: "If it ___ tomorrow, we'll stay at home.", a: ["rains", "will rain", "rained"], c: 0 },
    { q: "I ___ watching TV when you called.", a: ["was", "were", "did"], c: 0 }, { q: "This is the ___ expensive hotel in the city.", a: ["most", "more", "much"], c: 0 }
  ]
};
})();

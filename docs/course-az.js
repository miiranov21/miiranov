// Курс азербайджанского для русскоговорящих: с нуля до базового уровня (A1 → A2).
// Формат как у английского курса. Варианты в quiz перемешиваются при показе.
(window.MD_COURSES = window.MD_COURSES || {}).az = {
  id: "az",
  name: "Азербайджанский",
  voice: "az-AZ",
  voiceRequired: true,          // без азербайджанского голоса на устройстве задания на слух не показываются
  target: "по-азербайджански",
  fold: true,                   // при вводе с клавиатуры ə=e, ı=i, ş=s, ç=c, ğ=g, ö=o, ü=u
  placement: [
    { q: "Что значит «Salam»?", a: ["привет", "спасибо", "пока"], c: 0 },
    { q: "Mən tələbə___. (Я студент.)", a: ["yəm", "san", "dir"], c: 0 },
    { q: "Что значит «Sağ ol»?", a: ["спасибо", "пожалуйста", "извините"], c: 0 },
    { q: "Bu ___dir? (Что это?)", a: ["nə", "kim", "harada"], c: 0 },
    { q: "Dünən mən evdə ___. (Вчера я был дома.)", a: ["idim", "idin", "idi"], c: 0 },
    { q: "Mən çay iç___. (Я пью чай.)", a: ["irəm", "ir", "irsən"], c: 0 },
    { q: "Kitab masa___. (Книга на столе.)", a: ["dadır", "dan", "ya"], c: 0 },
    { q: "Mən ət ye___. (Я не ем мясо.)", a: ["mirəm", "yirəm", "deyiləm"], c: 0 },
    { q: "Sabah biz kinoya ___. (Завтра мы пойдём в кино.)", a: ["gedəcəyik", "getdik", "gedirdik"], c: 0 },
    { q: "Mən Bakıda beş ildir ___. (Я живу в Баку пять лет.)", a: ["yaşayıram", "yaşadım", "yaşayacağam"], c: 0 },
    { q: "Vaxtım olsa, səyahət ___. (Если будет время, я поеду путешествовать.)", a: ["edərəm", "etdim", "edirdim"], c: 0 },
    { q: "Что значит «mümkündür»?", a: ["возможно", "невозможно", "обязательно"], c: 0 }
  ],
  units: [
    {
      id: "az1", icon: "👋", title: "Приветствия",
      words: [["salam", "привет"], ["hələlik", "пока"], ["sağ ol", "спасибо"], ["xahiş edirəm", "пожалуйста"], ["bəli", "да"],
              ["xeyr", "нет"], ["bağışlayın", "извините"], ["sabahınız xeyir", "доброе утро"], ["gecəniz xeyrə qalsın", "спокойной ночи"], ["dost", "друг"]],
      phrases: [["Necəsən?", "Как ты?"], ["Yaxşıyam, sağ ol.", "У меня всё хорошо, спасибо."],
                ["Tanış olmağıma şadam.", "Приятно познакомиться."], ["Görüşənədək!", "До встречи!"]],
      grammar: {
        title: "«Я есть»: окончания -am, -san, -dır",
        text: "Отдельного слова «быть» нет. К слову добавляют окончание: mən — -am/-əm (после гласной -yam/-yəm), sən — -san/-sən, o — -dır/-dir/-dur/-dür. Гласная окончания подстраивается под слово.",
        examples: [["Mən tələbəyəm.", "Я студент."], ["Sən mənim dostumsan.", "Ты мой друг."], ["O həkimdir.", "Он врач."]]
      },
      quiz: [
        { q: "Mən tələbə___.", a: ["yəm", "san", "dir"], c: 0 },
        { q: "Sən yaxşı___?", a: ["san", "yam", "dır"], c: 0 },
        { q: "O həkim___.", a: ["dir", "əm", "sən"], c: 0 }
      ]
    },
    {
      id: "az2", icon: "👨‍👩‍👧", title: "Семья",
      words: [["ana", "мама"], ["ata", "папа"], ["bacı", "сестра"], ["qardaş", "брат"], ["ailə", "семья"],
              ["ad", "имя"], ["kişi", "мужчина"], ["qadın", "женщина"], ["uşaq", "ребёнок"], ["ər", "муж"]],
      phrases: [["Mənim adım Annadır.", "Меня зовут Анна."], ["Bu mənim qardaşımdır.", "Это мой брат."],
                ["O mənim bacımdır.", "Она моя сестра."], ["Mən ailəmi sevirəm.", "Я люблю свою семью."]],
      grammar: {
        title: "Мой, твой, его: окончания принадлежности",
        text: "«Мой» — окончание -ım/-im/-um/-üm (после гласной просто -m), «твой» — -ın/-in/-un/-ün (после гласной -n), «его, её» — -ı/-i/-u/-ü (после гласной -sı/-si). Слова mənim, sənin, onun можно добавить для ясности.",
        examples: [["mənim adım", "моё имя"], ["sənin anan", "твоя мама"], ["onun atası", "его папа"]]
      },
      quiz: [
        { q: "mənim ad___ (моё имя)", a: ["ım", "ın", "ı"], c: 0 },
        { q: "sənin ana___ (твоя мама)", a: ["n", "m", "sı"], c: 0 },
        { q: "onun ata___ (его папа)", a: ["sı", "m", "n"], c: 0 }
      ]
    },
    {
      id: "az3", icon: "🔢", title: "Числа и время",
      words: [["bir", "один"], ["iki", "два"], ["üç", "три"], ["beş", "пять"], ["on", "десять"],
              ["bu gün", "сегодня"], ["sabah", "завтра"], ["səhər", "утро"], ["axşam", "вечер"], ["saat", "час"]],
      phrases: [["Mənim iki bacım var.", "У меня две сестры."], ["Sabah görüşərik.", "Увидимся завтра."],
                ["Saat neçədir?", "Который час?"], ["Saat beşdir.", "Сейчас пять часов."]],
      grammar: {
        title: "Множественное число: -lar и -lər",
        text: "После a, ı, o, u ставят -lar, после e, ə, i, ö, ü — -lər: kitab → kitablar, ev → evlər. Но после числа множественное не ставят: üç kitab — три книги.",
        examples: [["kitablar", "книги"], ["evlər", "дома"], ["beş uşaq", "пять детей"]]
      },
      quiz: [
        { q: "ev___ (дома́)", a: ["lər", "lar", "ı"], c: 0 },
        { q: "Üç ___ (три книги)", a: ["kitab", "kitablar", "kitablər"], c: 0 },
        { q: "uşaq___ (дети)", a: ["lar", "lər", "ım"], c: 0 }
      ]
    },
    {
      id: "az4", icon: "🍎", title: "Еда",
      words: [["su", "вода"], ["çörək", "хлеб"], ["alma", "яблоко"], ["qəhvə", "кофе"], ["çay", "чай"],
              ["süd", "молоко"], ["yumurta", "яйцо"], ["pendir", "сыр"], ["səhər yeməyi", "завтрак"], ["şam yeməyi", "ужин"]],
      phrases: [["Bir çay, xahiş edirəm.", "Один чай, пожалуйста."], ["Mən hər gün alma yeyirəm.", "Я ем яблоко каждый день."],
                ["Su soyuqdur.", "Вода холодная."], ["Şam yeməyinə nə var?", "Что на ужин?"]],
      grammar: {
        title: "Есть и нет: var и yox",
        text: "«Есть» — var, «нет» — yox (yoxdur). «У меня есть» говорят Məndə … var или через принадлежность: Mənim maşınım var — у меня есть машина.",
        examples: [["Çörək var.", "Хлеб есть."], ["Süd yoxdur.", "Молока нет."], ["Məndə alma var.", "У меня есть яблоко."]]
      },
      quiz: [
        { q: "Evdə çörək ___. (Дома есть хлеб.)", a: ["var", "yox", "bəli"], c: 0 },
        { q: "Süd ___. (Молока нет.)", a: ["yoxdur", "vardır", "deyil"], c: 0 },
        { q: "Məndə alma ___. (У меня есть яблоко.)", a: ["var", "yox", "dır"], c: 0 }
      ]
    },
    {
      id: "az5", icon: "🏠", title: "Дом",
      words: [["ev", "дом"], ["otaq", "комната"], ["mətbəx", "кухня"], ["çarpayı", "кровать"], ["masa", "стол"],
              ["qapı", "дверь"], ["pəncərə", "окно"], ["stul", "стул"], ["böyük", "большой"], ["kiçik", "маленький"]],
      phrases: [["Mətbəx böyükdür.", "Кухня большая."], ["Mənim otağım kiçikdir.", "Моя комната маленькая."],
                ["Otaqda masa var.", "В комнате есть стол."], ["Pəncərəni açın, xahiş edirəm.", "Откройте окно, пожалуйста."]],
      grammar: {
        title: "Где? Окончание -da / -də",
        text: "Чтобы сказать «в, на», к слову добавляют -da (после a, ı, o, u) или -də (после e, ə, i, ö, ü): otaq → otaqda (в комнате), ev → evdə (дома).",
        examples: [["Mən evdəyəm.", "Я дома."], ["Kitab masadadır.", "Книга на столе."], ["Ana mətbəxdədir.", "Мама на кухне."]]
      },
      quiz: [
        { q: "Mən ev___. (Я дома.)", a: ["dəyəm", "dayam", "dən"], c: 0 },
        { q: "Kitab masa___. (Книга на столе.)", a: ["dadır", "dədir", "ya"], c: 0 },
        { q: "Uşaq otaq___. (Ребёнок в комнате.)", a: ["dadır", "dədir", "a"], c: 0 }
      ]
    },
    {
      id: "az6", icon: "🏃", title: "Действия",
      words: [["getmək", "идти"], ["yemək", "есть"], ["içmək", "пить"], ["oxumaq", "читать"], ["yatmaq", "спать"],
              ["işləmək", "работать"], ["öyrənmək", "учить"], ["qaçmaq", "бегать"], ["sevmək", "любить"], ["istəmək", "хотеть"]],
      phrases: [["Mən kitab oxumağı sevirəm.", "Я люблю читать книги."], ["Biz işə gedirik.", "Мы идём на работу."],
                ["O səhər çay içir.", "Она пьёт чай утром."], ["O yatmaq istəyir.", "Он хочет спать."]],
      grammar: {
        title: "Настоящее время: -ır / -ir / -ur / -ür",
        text: "Убираем -maq/-mək, добавляем -ır/-ir/-ur/-ür и окончание лица: mən içirəm (я пью), sən içirsən, o içir, biz içirik. Если основа на гласную, вставляется -y-: oxu → oxuyur.",
        examples: [["Mən işləyirəm.", "Я работаю."], ["O kitab oxuyur.", "Он читает книгу."], ["Biz çay içirik.", "Мы пьём чай."]]
      },
      quiz: [
        { q: "Mən çay iç___.", a: ["irəm", "irsən", "irik"], c: 0 },
        { q: "Sən nə oxu___?", a: ["yursan", "yuram", "yuruq"], c: 0 },
        { q: "O işə ged___.", a: ["ir", "irəm", "irik"], c: 0 }
      ]
    },
    {
      id: "az7", icon: "🏙", title: "Город",
      words: [["küçə", "улица"], ["mağaza", "магазин"], ["maşın", "машина"], ["avtobus", "автобус"], ["park", "парк"],
              ["şəhər", "город"], ["sola", "налево"], ["sağa", "направо"], ["yaxın", "близко"], ["uzaq", "далеко"]],
      phrases: [["Mağaza haradadır?", "Где магазин?"], ["Sola dönün.", "Поверните налево."],
                ["Park evimə yaxındır.", "Парк рядом с моим домом."], ["Vağzala necə gedim?", "Как мне пройти к вокзалу?"]],
      grammar: {
        title: "Вопросы: harada, nə, necə, kim",
        text: "harada — где, nə — что, necə — как, kim — кто. Вопросительное слово обычно стоит перед глаголом или в конце фразы: Avtobus haradadır? — Где автобус?",
        examples: [["Avtobus haradadır?", "Где автобус?"], ["Bu nədir?", "Что это?"], ["O kimdir?", "Кто он?"]]
      },
      quiz: [
        { q: "Park ___dır? — Yaxındır.", a: ["harada", "nə", "kim"], c: 0 },
        { q: "Bu ___dir? (Что это?)", a: ["nə", "kim", "necə"], c: 0 },
        { q: "O ___dir? (Кто он?)", a: ["kim", "nə", "harada"], c: 0 }
      ]
    },
    {
      id: "az8", icon: "📅", title: "Мой день",
      words: [["bazar ertəsi", "понедельник"], ["cümə", "пятница"], ["bazar", "воскресенье"], ["həftə", "неделя"], ["gün", "день"],
              ["həmişə", "всегда"], ["tez-tez", "часто"], ["heç vaxt", "никогда"], ["tez", "рано"], ["gec", "поздно"]],
      phrases: [["Mən həmişə tez dururam.", "Я всегда встаю рано."], ["Bazar günü istirahət edirik.", "В воскресенье мы отдыхаем."],
                ["Axşamlar tez-tez kitab oxuyuram.", "По вечерам я часто читаю."], ["O heç vaxt gecikmir.", "Она никогда не опаздывает."]],
      grammar: {
        title: "Порядок слов: глагол в конце",
        text: "Глагол обычно стоит в конце предложения: Mən kitab oxuyuram — дословно «Я книгу читаю». С heç vaxt (никогда) глагол ставят в отрицательной форме: heç vaxt gecikmir.",
        examples: [["Mən çay içirəm.", "Я пью чай."], ["O hər gün qaçır.", "Он бегает каждый день."], ["Biz heç vaxt gecikmirik.", "Мы никогда не опаздываем."]]
      },
      quiz: [
        { q: "Где обычный порядок слов?", a: ["Mən kitab oxuyuram.", "Oxuyuram mən kitab.", "Kitab mən oxuyuram mən."], c: 0 },
        { q: "O heç vaxt ___. (Она никогда не опаздывает.)", a: ["gecikmir", "gecikir", "gecikirəm"], c: 0 },
        { q: "Mən həmişə tez ___. (Я всегда встаю рано.)", a: ["dururam", "durur", "durursan"], c: 0 }
      ]
    },
    {
      id: "az9", icon: "💪", title: "Самочувствие",
      words: [["xoşbəxt", "счастливый"], ["kədərli", "грустный"], ["yorğun", "уставший"], ["ac", "голодный"], ["xəstə", "больной"],
              ["sağlam", "здоровый"], ["güclü", "сильный"], ["yaxşı", "хороший"], ["hiss etmək", "чувствовать"], ["idman", "спорт"]],
      phrases: [["Mən bu gün yorğunam.", "Я сегодня устал."], ["Sən acsan?", "Ты голоден?"],
                ["Özümü yaxşı hiss etmirəm.", "Я плохо себя чувствую."], ["İdman sağlamlıq üçün faydalıdır.", "Спорт полезен для здоровья."]],
      grammar: {
        title: "Отрицание: -ma / -mə и deyil",
        text: "У глаголов отрицание — -ma/-mə после основы: içirəm (пью) → içmirəm (не пью). У слов без глагола — deyil: Mən ac deyiləm (я не голоден).",
        examples: [["Mən qəhvə içmirəm.", "Я не пью кофе."], ["O xəstə deyil.", "Он не болен."], ["Biz bu gün işləmirik.", "Мы сегодня не работаем."]]
      },
      quiz: [
        { q: "Mən ac ___. (Я не голоден.)", a: ["deyiləm", "yoxam", "mirəm"], c: 0 },
        { q: "Mən ət ye___. (Я не ем мясо.)", a: ["mirəm", "yirəm", "deyiləm"], c: 0 },
        { q: "O xəstə ___. (Он не болен.)", a: ["deyil", "yox", "mir"], c: 0 }
      ]
    },
    {
      id: "az10", icon: "⏪", title: "Вчера и раньше",
      words: [["dünən", "вчера"], ["getdim", "я пошёл"], ["gördüm", "я видел"], ["yedim", "я поел"], ["aldım", "я купил"],
              ["etdim", "я сделал"], ["idi", "был, была"], ["əvvəl", "раньше, назад"], ["keçən həftə", "на прошлой неделе"], ["artıq", "уже"]],
      phrases: [["Dünən parka getdim.", "Вчера я ходил в парк."], ["Biz yaxşı bir film gördük.", "Мы посмотрели хороший фильм."],
                ["Sən yemək yedin?", "Ты поел?"], ["Keçən həftə evdə idim.", "На прошлой неделе я был дома."]],
      grammar: {
        title: "Прошедшее время: -dı / -di / -du / -dü",
        text: "К основе глагола добавляют -dı/-di/-du/-dü и окончание лица: mən getdim (я пошёл), sən getdin, o getdi, biz getdik, siz getdiniz, onlar getdilər.",
        examples: [["Mən dünən işlədim.", "Вчера я работал."], ["O evə getdi.", "Она пошла домой."], ["Sən bunu gördün?", "Ты это видел?"]]
      },
      quiz: [
        { q: "Dünən mən mağazaya get___.", a: ["dim", "din", "di"], c: 0 },
        { q: "Sən filmi gör___?", a: ["dün", "düm", "dük"], c: 0 },
        { q: "Biz dünən evdə ___. (были)", a: ["idik", "idim", "idi"], c: 0 }
      ]
    }
  ]
};

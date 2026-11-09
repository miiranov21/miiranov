// Программа английского по месяцам: A0 → C2 при 45 минутах в день, 6 дней в неделю.
// Уровень подтверждается только экзаменом уровня (конец 3, 6, 12, 20, 28 и 36 месяца).
// Материалы месяцев лежат в отдельных файлах program-en-m<N>.js и добавляются в months[N-1].weeks / exam.
(window.MD_PROGRAM = window.MD_PROGRAM || {}).en = {
  id: "en",
  minutes: 45,
  levelExams: { 3: "A1", 6: "A2", 12: "B1", 20: "B2", 28: "C1", 36: "C2" },
  passTotal: 70,      // экзамен: не меньше 70% в сумме
  passSection: 60,    // и не меньше 60% в каждом навыке
  retakeHours: 24,    // пересдача не раньше чем через сутки
  honesty: "45 минут в день — это примерно 20 часов в месяц. Для A2 нужно около 180–200 часов занятий, для B1 — около 350–400, для B2 — около 500–600, для C1 — около 700–800, для C2 — 1000–1200 и больше. Поэтому к приложению каждую неделю добавлена практика вне его: слушать, читать, говорить. Без неё B1 и выше к указанным месяцам не получатся, а C1 и C2 требуют ещё и живого общения с носителями или учителем, который проверяет речь и тексты.",
  levels: {
    A1: { months: [1, 3], can: {
      listen: "Понимаешь медленную чёткую речь о себе, семье, доме, времени и покупках.",
      read: "Читаешь короткие простые тексты: объявления, анкеты, сообщения.",
      speak: "Представляешься, отвечаешь на простые вопросы, спрашиваешь дорогу и время.",
      write: "Заполняешь анкету, пишешь короткое сообщение о себе."
    }},
    A2: { months: [4, 6], can: {
      listen: "Понимаешь главное в коротких разговорах на бытовые темы: магазин, транспорт, работа.",
      read: "Читаешь простые письма, меню, расписания, короткие истории.",
      speak: "Справляешься в магазине, кафе, гостинице; рассказываешь о прошлом и планах.",
      write: "Пишешь короткие письма и истории о своём опыте."
    }},
    B1: { months: [7, 12], can: {
      listen: "Понимаешь основное в разговорах и видео на знакомые темы при обычном темпе.",
      read: "Читаешь статьи и тексты о повседневной жизни и работе.",
      speak: "Объясняешься почти в любой бытовой ситуации за границей, высказываешь мнение.",
      write: "Пишешь связные письма и тексты, описываешь опыт и впечатления."
    }},
    B2: { months: [13, 20], can: {
      listen: "Понимаешь фильмы, новости и живую речь носителей на большинство тем.",
      read: "Читаешь статьи и рабочие документы, понимаешь позицию автора.",
      speak: "Свободно общаешься с носителями, участвуешь в обсуждениях, проходишь собеседование.",
      write: "Пишешь подробные тексты, эссе и деловые письма."
    }},
    C1: { months: [21, 28], can: {
      listen: "Понимаешь длинную речь, лекции и фильмы, даже когда мысль выражена не прямо.",
      read: "Читаешь сложные статьи, отчёты и художественную литературу, замечаешь стиль и подтекст.",
      speak: "Говоришь бегло и спонтанно, точно подбираешь слова для работы, учёбы и споров.",
      write: "Пишешь чёткие, хорошо выстроенные тексты на сложные темы: эссе, отчёты, статьи."
    }},
    C2: { months: [29, 36], can: {
      listen: "Без усилий понимаешь любую речь: быстрые носители, акценты, юмор, намёки.",
      read: "Читаешь любые тексты, включая абстрактные, научные и литературные.",
      speak: "Выражаешь мысль спонтанно и очень точно, передаёшь тончайшие оттенки смысла.",
      write: "Пишешь сложные тексты в нужном стиле: статьи, рецензии, профессиональные документы."
    }}
  },
  // практика вне приложения: по 4 задания в неделю (слушать, читать, говорить, писать), чередуются по неделям
  practice: {
   "A1": {
    "listen": [
     {
      "t": "Посмотри серию «Peppa Pig» на английском (около 5 минут) два раза: сначала без субтитров, потом с английскими. Выпиши 5 новых слов в «Мой словарь».",
      "l": [
       [
        "YouTube: Peppa Pig на английском",
        "https://www.youtube.com/results?search_query=peppa+pig+english+full+episodes"
       ]
      ]
     },
     {
      "t": "British Council → раздел Skills → Listening → A1: выбери одно аудио, послушай и сделай упражнения под ним.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "Найди на YouTube «English listening practice for beginners», послушай 10 минут и повторяй фразы вслух.",
      "l": [
       [
        "YouTube: listening для начинающих",
        "https://www.youtube.com/results?search_query=english+listening+practice+for+beginners+A1"
       ]
      ]
     }
    ],
    "read": [
     {
      "t": "British Council → Skills → Reading → A1: прочитай один текст и сделай задания.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "English E-Reader: выбери книгу уровня Starter или Beginner и прочитай 1 главу.",
      "l": [
       [
        "English E-Reader",
        "https://english-e-reader.net/"
       ]
      ]
     },
     {
      "t": "Breaking News English: выбери новость уровня 0 или 1, прочитай и послушай её.",
      "l": [
       [
        "Breaking News English",
        "https://breakingnewsenglish.com/"
       ]
      ]
     }
    ],
    "speak": [
     {
      "t": "Запиши на диктофон 1 минуту о себе по теме недели «{topic}». Послушай запись. Слова, в которых сомневаешься, проверь в YouGlish: там их произносят носители.",
      "l": [
       [
        "YouGlish (произношение)",
        "https://youglish.com/"
       ]
      ]
     },
     {
      "t": "Шэдоуинг: открой диалог из урока «Аудирование» этой недели и повторяй каждую фразу сразу за диктором по 3 раза.",
      "l": []
     },
     {
      "t": "Найди собеседника в Tandem или HelloTalk и обменяйся 5 голосовыми сообщениями о себе.",
      "l": [
       [
        "Tandem",
        "https://www.tandem.net/"
       ],
       [
        "HelloTalk",
        "https://www.hellotalk.com/"
       ]
      ]
     }
    ],
    "write": [
     {
      "t": "Напиши 5 предложений по теме недели «{topic}» и проверь их в LanguageTool.",
      "l": [
       [
        "LanguageTool (проверка текста)",
        "https://languagetool.org/"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Writing → A1: выполни одно задание (анкета, сообщение, открытка).",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     }
    ]
   },
   "A2": {
    "listen": [
     {
      "t": "British Council → Skills → Listening → A2: одно аудио с упражнениями.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "News in Levels: новость уровня 1 или 2 — сначала послушай без текста, потом прочитай.",
      "l": [
       [
        "News in Levels",
        "https://www.newsinlevels.com/"
       ]
      ]
     },
     {
      "t": "Посмотри серию ситкома «Extr@ English» с английскими субтитрами. Выпиши 5 фраз, которые пригодятся в жизни.",
      "l": [
       [
        "YouTube: Extr@ English",
        "https://www.youtube.com/results?search_query=extra+english+episode+1"
       ]
      ]
     }
    ],
    "read": [
     {
      "t": "British Council → Skills → Reading → A2: один текст с заданиями.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "English E-Reader: книга уровня Elementary, 2 главы. Незнакомые слова — в «Мой словарь».",
      "l": [
       [
        "English E-Reader",
        "https://english-e-reader.net/"
       ]
      ]
     },
     {
      "t": "Breaking News English: новость уровня 2, прочитай и ответь на вопросы под ней.",
      "l": [
       [
        "Breaking News English",
        "https://breakingnewsenglish.com/"
       ]
      ]
     }
    ],
    "speak": [
     {
      "t": "Расскажи на диктофон за 2 минуты, что ты делал в выходные. Тема недели «{topic}» — используй её слова.",
      "l": [
       [
        "YouGlish (произношение)",
        "https://youglish.com/"
       ]
      ]
     },
     {
      "t": "Созвонись на 10 минут с собеседником в Tandem или HelloTalk.",
      "l": [
       [
        "Tandem",
        "https://www.tandem.net/"
       ],
       [
        "HelloTalk",
        "https://www.hellotalk.com/"
       ]
      ]
     },
     {
      "t": "Открой 3 фото в галерее телефона и опиши каждое вслух по-английски (что на фото, где, когда).",
      "l": []
     }
    ],
    "write": [
     {
      "t": "Напиши сообщение другу на 60–80 слов по теме «{topic}» и проверь в LanguageTool.",
      "l": [
       [
        "LanguageTool (проверка текста)",
        "https://languagetool.org/"
       ]
      ]
     },
     {
      "t": "Опубликуй короткий текст (5–8 предложений) в r/WriteStreakEN: носители бесплатно поправят ошибки.",
      "l": [
       [
        "Reddit r/WriteStreakEN",
        "https://www.reddit.com/r/WriteStreakEN/"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Writing → A2: одно задание.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     }
    ]
   },
   "B1": {
    "listen": [
     {
      "t": "BBC 6 Minute English: один выпуск. Сначала послушай без текста, потом с транскриптом под видео.",
      "l": [
       [
        "BBC 6 Minute English",
        "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Listening → B1: одно аудио с упражнениями.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "Подкаст All Ears English: один выпуск (15–20 минут). Выпиши 3 разговорные фразы.",
      "l": [
       [
        "All Ears English",
        "https://www.allearsenglish.com/"
       ]
      ]
     },
     {
      "t": "2 серии «Friends» или другого сериала с английскими субтитрами.",
      "l": []
     }
    ],
    "read": [
     {
      "t": "News in Levels: новость уровня 3. Перескажи её вслух в 3–4 предложениях.",
      "l": [
       [
        "News in Levels",
        "https://www.newsinlevels.com/"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Reading → B1: один текст с заданиями.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "English E-Reader: книга уровня Pre-Intermediate или Intermediate, 1–2 главы.",
      "l": [
       [
        "English E-Reader",
        "https://english-e-reader.net/"
       ]
      ]
     }
    ],
    "speak": [
     {
      "t": "Разговор 20–30 минут с собеседником (Tandem, HelloTalk) или с учителем (italki, Preply). Тема — «{topic}».",
      "l": [
       [
        "Tandem",
        "https://www.tandem.net/"
       ],
       [
        "HelloTalk",
        "https://www.hellotalk.com/"
       ],
       [
        "italki",
        "https://www.italki.com/"
       ],
       [
        "Preply",
        "https://preply.com/"
       ]
      ]
     },
     {
      "t": "Перескажи вслух выпуск 6 Minute English за 2 минуты и запиши себя.",
      "l": [
       [
        "BBC 6 Minute English",
        "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"
       ]
      ]
     },
     {
      "t": "Запиши голосом своё мнение на 2 минуты по теме недели «{topic}»: «I think… because…».",
      "l": []
     }
    ],
    "write": [
     {
      "t": "Напиши текст на 120 слов по теме «{topic}» и опубликуй в r/WriteStreakEN для проверки носителями.",
      "l": [
       [
        "Reddit r/WriteStreakEN",
        "https://www.reddit.com/r/WriteStreakEN/"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Writing → B1: одно задание (письмо, эссе, отзыв).",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "Дневник: каждый вечер этой недели 5 предложений о прошедшем дне. В конце недели проверь всё в LanguageTool.",
      "l": [
       [
        "LanguageTool (проверка текста)",
        "https://languagetool.org/"
       ]
      ]
     }
    ]
   },
   "B2": {
    "listen": [
     {
      "t": "Luke's English Podcast: один выпуск без транскрипта. Запиши 5 выражений.",
      "l": [
       [
        "Luke's English Podcast",
        "https://teacherluke.co.uk/"
       ]
      ]
     },
     {
      "t": "TED: выступление до 15 минут с английскими субтитрами, потом пересмотри без субтитров.",
      "l": [
       [
        "TED Talks",
        "https://www.ted.com/talks"
       ]
      ]
     },
     {
      "t": "BBC The English We Speak: 3 коротких выпуска о живых выражениях.",
      "l": [
       [
        "BBC Learning English",
        "https://www.bbc.co.uk/learningenglish/"
       ]
      ]
     },
     {
      "t": "Серия сериала без русских субтитров (можно с английскими).",
      "l": []
     }
    ],
    "read": [
     {
      "t": "The Guardian: одна статья по теме недели «{topic}». Выпиши 10 сочетаний слов.",
      "l": [
       [
        "The Guardian",
        "https://www.theguardian.com/international"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Reading → B2: один текст с заданиями.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "BBC News: 2 новости. Перескажи каждую в 3 предложениях.",
      "l": [
       [
        "BBC News",
        "https://www.bbc.com/news"
       ]
      ]
     }
    ],
    "speak": [
     {
      "t": "Урок или разговор с учителем 30+ минут (italki, Preply). Попроси исправлять ошибки.",
      "l": [
       [
        "italki",
        "https://www.italki.com/"
       ],
       [
        "Preply",
        "https://preply.com/"
       ]
      ]
     },
     {
      "t": "Перескажи TED-выступление за 3 минуты и запиши себя. Сравни с оригиналом.",
      "l": [
       [
        "TED Talks",
        "https://www.ted.com/talks"
       ]
      ]
     },
     {
      "t": "Запиши 3-минутное мнение по теме «{topic}» с аргументами «за» и «против».",
      "l": []
     }
    ],
    "write": [
     {
      "t": "Эссе на 180 слов по теме «{topic}». Проверь в LanguageTool, потом опубликуй в r/WriteStreakEN.",
      "l": [
       [
        "LanguageTool (проверка текста)",
        "https://languagetool.org/"
       ],
       [
        "Reddit r/WriteStreakEN",
        "https://www.reddit.com/r/WriteStreakEN/"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Writing → B2: одно задание.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "Cambridge English (B2 First): найди бесплатные примеры заданий Writing и выполни одно.",
      "l": [
       [
        "Cambridge English: подготовка к экзаменам",
        "https://www.cambridgeenglish.org/"
       ]
      ]
     }
    ]
   },
   "C1": {
    "listen": [
     {
      "t": "BBC Radio 4 «In Our Time»: один выпуск (45 минут) без текста. Запиши 3 главные мысли.",
      "l": [
       [
        "BBC Radio 4: In Our Time",
        "https://www.bbc.co.uk/programmes/b006qykl"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Listening → C1: одно аудио с упражнениями.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "TED: выступление 15–20 минут без субтитров. Пересмотри сложные места.",
      "l": [
       [
        "TED Talks",
        "https://www.ted.com/talks"
       ]
      ]
     }
    ],
    "read": [
     {
      "t": "Guardian Long Read: одна большая статья. Перескажи её позицию автора в 5 предложениях.",
      "l": [
       [
        "Guardian: The Long Read",
        "https://www.theguardian.com/news/series/the-long-read"
       ]
      ]
     },
     {
      "t": "British Council → Skills → Reading → C1: один текст с заданиями.",
      "l": [
       [
        "British Council LearnEnglish",
        "https://learnenglish.britishcouncil.org/"
       ]
      ]
     },
     {
      "t": "Глава книги в оригинале (бесплатные классические книги — Project Gutenberg).",
      "l": [
       [
        "Project Gutenberg (бесплатные книги)",
        "https://www.gutenberg.org/"
       ]
      ]
     }
    ],
    "speak": [
     {
      "t": "Обсуждение сложной темы с носителем или учителем 45+ минут (italki, Preply). Тема — «{topic}».",
      "l": [
       [
        "italki",
        "https://www.italki.com/"
       ],
       [
        "Preply",
        "https://preply.com/"
       ]
      ]
     },
     {
      "t": "Подготовь и запиши выступление на 5 минут по теме недели «{topic}», как на презентации.",
      "l": []
     }
    ],
    "write": [
     {
      "t": "Эссе на 250+ слов по теме «{topic}». Отдай на проверку учителю или в r/WriteStreakEN.",
      "l": [
       [
        "Reddit r/WriteStreakEN",
        "https://www.reddit.com/r/WriteStreakEN/"
       ],
       [
        "italki",
        "https://www.italki.com/"
       ]
      ]
     },
     {
      "t": "Cambridge English (C1 Advanced): бесплатные примеры заданий Writing, выполни одно.",
      "l": [
       [
        "Cambridge English: подготовка к экзаменам",
        "https://www.cambridgeenglish.org/"
       ]
      ]
     }
    ]
   },
   "C2": {
    "listen": [
     {
      "t": "Стендап британского комика без субтитров: попробуй понять все шутки.",
      "l": [
       [
        "YouTube: British stand-up",
        "https://www.youtube.com/results?search_query=british+stand+up+comedy"
       ]
      ]
     },
     {
      "t": "BBC Radio 4 «In Our Time»: выпуск на незнакомую тему.",
      "l": [
       [
        "BBC Radio 4: In Our Time",
        "https://www.bbc.co.uk/programmes/b006qykl"
       ]
      ]
     }
    ],
    "read": [
     {
      "t": "Художественная книга в оригинале, 30–50 страниц (бесплатная классика на Project Gutenberg).",
      "l": [
       [
        "Project Gutenberg (бесплатные книги)",
        "https://www.gutenberg.org/"
       ]
      ]
     },
     {
      "t": "Guardian Long Read: статья. Найди в ней иронию и приёмы автора.",
      "l": [
       [
        "Guardian: The Long Read",
        "https://www.theguardian.com/news/series/the-long-read"
       ]
      ]
     }
    ],
    "speak": [
     {
      "t": "Выступи перед людьми по-английски: клуб Toastmasters в твоём городе или онлайн.",
      "l": [
       [
        "Toastmasters (клубы ораторов)",
        "https://www.toastmasters.org/"
       ]
      ]
     },
     {
      "t": "Дискуссия с носителем 60 минут на абстрактную тему (italki).",
      "l": [
       [
        "italki",
        "https://www.italki.com/"
       ]
      ]
     }
    ],
    "write": [
     {
      "t": "Рецензия или статья на 300 слов по теме «{topic}» и разбор с учителем.",
      "l": [
       [
        "italki",
        "https://www.italki.com/"
       ]
      ]
     },
     {
      "t": "Cambridge English (C2 Proficiency): бесплатные примеры заданий, выполни одно Writing.",
      "l": [
       [
        "Cambridge English: подготовка к экзаменам",
        "https://www.cambridgeenglish.org/"
       ]
      ]
     }
    ]
   }
  },
  months: [
    { n: 1, level: "A1", title: "Знакомство и основы", topics: ["Знакомство", "Семья", "Числа и время", "Мой дом"], grammar: ["to be: am, is, are", "my, your, his, her, this, that", "Множественное число", "there is / there are, a / an / the, предлоги места"] },
    { n: 2, level: "A1", title: "Повседневная жизнь", topics: ["Мой день", "Работа и люди", "Еда и магазин", "Свободное время"], grammar: ["Present Simple", "Present Simple: he / she, does / doesn't", "some / any, much / many", "can / can't, like + -ing, наречия частоты"] },
    { n: 3, level: "A1", title: "Город и прошлое", topics: ["Город и дорога", "Сейчас: одежда и погода", "Где ты был", "Выходные и отпуск"], grammar: ["Повелительное наклонение, предлоги", "Present Continuous", "was / were", "Past Simple"], examTitle: "Экзамен уровня A1" },
    { n: 4, level: "A2", title: "Покупки и сравнения", topics: ["Магазины и цены", "Одежда и размеры", "Кафе и ресторан", "Планы"], grammar: ["Сравнительная и превосходная степень", "too / enough", "I'd like, would you like", "be going to"] },
    { n: 5, level: "A2", title: "Путешествия", topics: ["Транспорт и билеты", "Гостиница", "История поездки", "Проблемы в пути"], grammar: ["Past Simple: вопросы и отрицания", "Past Continuous", "will для решений и обещаний", "must / have to"] },
    { n: 6, level: "A2", title: "Работа и здоровье", topics: ["Профессии и резюме", "У врача", "Опыт", "Советы"], grammar: ["Present Perfect: ever / never", "already / yet / just", "should / shouldn't", "First Conditional"], examTitle: "Экзамен уровня A2" },
    { n: 7, level: "B1", title: "Опыт и истории", topics: ["Жизненный опыт", "Детство", "Рассказ о событии", "Люди и характер"], grammar: ["Present Perfect и Past Simple", "for / since", "used to", "Наречия и порядок слов"] },
    { n: 8, level: "B1", title: "Планы и будущее", topics: ["Планы на жизнь", "Договориться о встрече", "Прогнозы", "Мечты"], grammar: ["will / going to / Present Continuous для будущего", "Придаточные времени: when, as soon as", "might / may", "Предлоги времени"] },
    { n: 9, level: "B1", title: "Общение и мнения", topics: ["Высказать мнение", "Согласиться и возразить", "Просьбы и предложения", "Отношения"], grammar: ["Модальные глаголы: should, ought to, had better", "Вежливые просьбы: could, would you mind", "so / such, too / enough", "Вопросительные хвосты"] },
    { n: 10, level: "B1", title: "Медиа и технологии", topics: ["Интернет и соцсети", "Новости", "Гаджеты", "Реклама"], grammar: ["Пассивный залог: Present и Past", "Относительные придаточные: who, which, that", "Косвенные вопросы", "Фразовые глаголы с get, take"] },
    { n: 11, level: "B1", title: "Общество и природа", topics: ["Город и деревня", "Экология", "Праздники и традиции", "Законы и правила"], grammar: ["Second Conditional", "Косвенная речь: введение", "Количественные слова: few, little, a lot of", "Артикли: обобщение"] },
    { n: 12, level: "B1", title: "Жизнь в другой стране", topics: ["Аренда жилья", "Банк и документы", "Работа и собеседование", "Соседи и быт"], grammar: ["Герундий и инфинитив", "Фразовые глаголы быта", "Формальное и неформальное письмо", "Повторение B1"], examTitle: "Экзамен уровня B1" },
    { n: 13, level: "B2", title: "Карьера", topics: ["Карьерный путь", "Собеседование", "Офис и коллеги", "Успех и неудачи"], grammar: ["Present Perfect Continuous", "Past Perfect", "Повествовательные времена", "Словообразование"] },
    { n: 14, level: "B2", title: "Деньги и выбор", topics: ["Финансы", "Покупки и потребление", "Сожаления", "Решения"], grammar: ["Third Conditional", "Смешанные условные", "wish / if only", "Связующие слова"] },
    { n: 15, level: "B2", title: "Наука и здоровье", topics: ["Медицина", "Исследования", "Спорт и тело", "Психология"], grammar: ["Пассив: все времена", "have / get something done", "Безличные конструкции: It is said that", "Сочетаемость слов"] },
    { n: 16, level: "B2", title: "Культура и искусство", topics: ["Кино и книги", "Музыка", "Путешествия и культуры", "Отзывы и рецензии"], grammar: ["Сложные относительные придаточные", "Причастные обороты", "Усилители и смягчители", "Написание отзыва"] },
    { n: 17, level: "B2", title: "Работа и переговоры", topics: ["Совещания", "Переговоры", "Презентации", "Деловая переписка"], grammar: ["Модальные глаголы предположения: must / might / can't have", "Вежливые формулировки", "Эмфаза: What I need is…", "Деловое письмо"] },
    { n: 18, level: "B2", title: "Общество и проблемы", topics: ["Образование", "Технологии и будущее", "Город и транспорт", "Глобальные проблемы"], grammar: ["Косвенная речь: полностью", "Глаголы передачи речи", "Эссе: аргументы и контраргументы", "Инверсия: never have I…"] },
    { n: 19, level: "B2", title: "Живая речь", topics: ["Фразовые глаголы", "Идиомы", "Разговорный стиль", "Юмор и сленг"], grammar: ["Фразовые глаголы с несколькими значениями", "Идиомы в контексте", "Регистр речи", "Сокращения в разговоре"] },
    { n: 20, level: "B2", title: "Готовность к жизни за границей", topics: ["Документы и госуслуги", "Врач и страховка", "Аренда и договор", "Пробный экзамен"], grammar: ["Повторение всех времён", "Повторение условных", "Формальное письмо и жалоба", "Пробный экзамен формата IELTS"], examTitle: "Экзамен уровня B2" },
    { n: 21, level: "C1", title: "Время и перемены", topics: ["Биографии", "Перемены в жизни", "Воспоминания", "Повороты карьеры"], grammar: ["Future Perfect и Future Continuous", "Повествовательные времена: тонкости", "would и used to о прошлом", "Глаголы состояния: оттенки"] },
    { n: 22, level: "C1", title: "Аргументация", topics: ["Дебаты", "Убеждение", "Этика", "Предвзятость в медиа"], grammar: ["Расщеплённые предложения: It is… that, What…", "Дискурсивные маркеры", "Уступительные: although, despite, whereas", "Смягчение высказываний (hedging)"] },
    { n: 23, level: "C1", title: "Наука и технологии", topics: ["Искусственный интеллект", "Прорывы в медицине", "Космос", "Приватность данных"], grammar: ["Номинализация", "Пассив в научном стиле", "Глаголы передачи мнения и их модели", "Академическая лексика"] },
    { n: 24, level: "C1", title: "Бизнес и экономика", topics: ["Стартапы", "Рынки", "Лидерство", "Сделки"], grammar: ["Условные без if: should, were, had", "would rather, it's time", "Модальные с перфектом", "Формальный регистр"] },
    { n: 25, level: "C1", title: "Культура и идентичность", topics: ["Идентичность", "Миграция", "Язык и культура", "Традиции и современность"], grammar: ["Причастные обороты: продвинутый уровень", "Относительные придаточные с предлогами", "Эллипсис и замещение", "Эмфатическое do"] },
    { n: 26, level: "C1", title: "Право и общество", topics: ["Законы", "Права человека", "Преступление и правосудие", "Политика"], grammar: ["Пассивные конструкции сообщения: is believed to", "Сослагательное: It's essential that he be", "Сложные именные группы", "Связки формального письма"] },
    { n: 27, level: "C1", title: "Психология и поведение", topics: ["Принятие решений", "Привычки", "Эмоции", "Отношения"], grammar: ["Устойчивые сочетания", "Фразовые глаголы: продвинутый уровень", "Усилительные наречия и их сочетаемость", "Смешанные условные: повторение"] },
    { n: 28, level: "C1", title: "Подготовка к C1", topics: ["Академическое письмо", "Презентация", "Пробный экзамен", "Повторение"], grammar: ["Повторение грамматики C1", "Структура эссе и отчёта", "Связность и логика текста", "Пробный экзамен формата CAE"], examTitle: "Экзамен уровня C1" },
    { n: 29, level: "C2", title: "Литература и стиль", topics: ["Анализ текста", "Голос рассказчика", "Поэзия", "Перевод"], grammar: ["Стилистическая инверсия", "Вынесение в начало (fronting)", "Времена в художественном тексте", "Риторические приёмы"] },
    { n: 30, level: "C2", title: "Философия и идеи", topics: ["Этика", "Свобода воли", "Знание", "Смысл"], grammar: ["Абстрактные существительные", "Сложные гипотезы", "Тонкая модальность", "Степени уверенности"] },
    { n: 31, level: "C2", title: "Журналистика и медиа", topics: ["Журналистские расследования", "Колонки мнений", "Сатира", "Заголовки"], grammar: ["Язык заголовков", "Смена регистра", "Ирония и преуменьшение", "Косвенная речь: оттенки"] },
    { n: 32, level: "C2", title: "Юмор, идиомы и сленг", topics: ["Юмор", "Британский и американский", "Сленг", "Игра слов"], grammar: ["Идиомы", "Каламбуры", "Разговорная грамматика", "Региональные варианты"] },
    { n: 33, level: "C2", title: "Профессиональное общение", topics: ["Дипломатия", "Разрешение конфликтов", "Публичные выступления", "Интервью"], grammar: ["Тактичные формулировки", "Смягчение и вежливость", "Приёмы убеждения", "Шкала формальности"] },
    { n: 34, level: "C2", title: "Мировые вызовы", topics: ["Климатическая политика", "Мировая экономика", "Здравоохранение", "Будущее работы"], grammar: ["Сложная аргументация", "Номинализация: продвинутый уровень", "Связность текста", "Точные количественные выражения"] },
    { n: 35, level: "C2", title: "История и цивилизация", topics: ["Империи", "Революции", "Как пишут историю", "Наследие"], grammar: ["Модальные предположения о прошлом", "Историческое настоящее", "Условные в рассуждениях об истории", "Сложные предложения"] },
    { n: 36, level: "C2", title: "Подготовка к C2", topics: ["Пробный экзамен", "Эссе", "Выступление", "Повторение"], grammar: ["Повторение грамматики C2", "Эссе и статья высокого уровня", "Устное выступление", "Пробный экзамен формата CPE"], examTitle: "Экзамен уровня C2" }
  ]
};

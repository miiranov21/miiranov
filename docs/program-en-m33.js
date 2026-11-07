// Месяц 33 (C2): Профессиональное общение. Дипломатия, конфликты, выступления, интервью.
(function(){
const M = window.MD_PROGRAM.en.months[32];
M.weeks = [
  {
    t: "Дипломатия",
    words: [
      ["envoy", "посланник, дипломатический представитель", "Энвой"], ["emissary", "эмиссар, доверенный посланец", "Эмисэри"], ["rapprochement", "сближение (между государствами)", "рэпрОшмон"], ["accord", "соглашение, договорённость", "экОд"], ["bilateral", "двусторонний", "байлЭтэрэл"],
      ["multilateral", "многосторонний", "малтилЭтэрэл"], ["overture", "примирительный шаг, инициатива", "Оувэчуэ"], ["brinkmanship", "балансирование на грани (войны, срыва)", "брИнкмэншип"], ["back channel", "неофициальный канал связи", "бэк чЭнл"], ["stalemate", "тупиковая ситуация, пат", "стЭйлмэйт"],
      ["concession", "уступка", "кэнсЭшн"], ["tit-for-tat", "ответный (по принципу «око за око»)", "тит-фэ-тЭт"], ["olive branch", "оливковая ветвь, предложение мира", "Олив бранч"], ["sovereignty", "суверенитет", "сОврэнти"], ["non-aggression pact", "пакт о ненападении", "нон-эгрЭшн пэкт"],
      ["entente", "согласие, союз (между государствами)", "онтОнт"], ["ratify", "ратифицировать", "рЭтифай"], ["broker", "выступать посредником (в сделке)", "брОукэ"], ["tread carefully", "действовать осторожно", "трэд кЭэфли"], ["save face", "сохранить лицо", "сэйв фэйс"],
      ["diplomatic immunity", "дипломатическая неприкосновенность", "диплэмЭтик имьЮнити"], ["persona non grata", "персона нон грата", "пёсОунэ нон грАтэ"], ["expel", "высылать (из страны)", "икспЭл"], ["communiqué", "официальное коммюнике", "кэмьЮникэй"], ["protocol", "протокол, этикет", "прОутэкол"],
      ["tacit", "молчаливый, негласный", "тЭсит"], ["conciliatory", "примирительный", "кэнсИлиэтэри"], ["intransigent", "непримиримый, неуступчивый", "интрЭнзиджэнт"], ["posturing", "позёрство, демонстративная поза", "пОсчэринг"], ["thaw", "потепление (в отношениях)", "со"]
    ],
    phrases: [["Let me put it another way.", "Позвольте сформулировать иначе."], ["I'm not sure that's quite the right approach.", "Не уверен, что это вполне правильный подход."], ["Perhaps we could find a form of words that works for both sides.", "Возможно, мы найдём формулировку, устраивающую обе стороны."], ["We would not rule out further talks.", "Мы не исключаем дальнейших переговоров."], ["I hear what you're saying, but...", "Я понимаю, о чём вы говорите, но..."], ["That may be a little premature.", "Возможно, это немного преждевременно."]],
    grammar: {
      title: "Тактичные формулировки",
      text: "Дипломатичный английский смягчает прямую оценку, не меняя её сути. Главный приём — отрицание плюс положительное слово вместо отрицательного: не «This is a bad idea», а «This may not be the best idea» или «I'm not entirely convinced». Второй приём — дистанцирование через прошедшее и длительное время: I was wondering whether..., We were hoping to... звучат мягче, чем I want. Третий — безличные и пассивные конструкции, которые убирают обвинение: «It appears that the deadline has been missed» вместо «You missed the deadline». Четвёртый — вводные «подушки»: with respect, I take your point, but..., if I may. Слова somewhat, rather, slightly снижают категоричность: «a somewhat ambitious timetable» фактически означает «нереалистичный график». Русскоязычные часто переводят дословно «Вы не правы» → «You are wrong», что по-английски звучит резко; лучше «I see it slightly differently». Помните также о подтексте: «With all due respect» часто предвещает жёсткое несогласие, а британское «I hear what you say» может означать «я не согласен».",
      examples: [["I'm not entirely convinced that this is the right moment.", "Я не до конца уверен, что сейчас подходящий момент."], ["We were wondering whether you might reconsider your position.", "Мы хотели бы узнать, не могли бы вы пересмотреть свою позицию."], ["It appears that some figures were left out of the report.", "Похоже, некоторые цифры не вошли в отчёт."], ["That may not be the most practical solution.", "Возможно, это не самое практичное решение."], ["I see it slightly differently, if I may.", "Позвольте, я смотрю на это немного иначе."]],
      quiz: [
        { q: "I'm not ___ convinced that this approach will work. (до конца)", a: ["entirely", "hardly", "barely"], c: 0 },
        { q: "We ___ wondering whether you could extend the deadline.", a: ["were", "are being", "had"], c: 0 },
        { q: "Instead of «You made a mistake»: It seems that a mistake ___ made.", a: ["was", "has", "did"], c: 0 },
        { q: "This may not be the ___ solution. (смягчение оценки)", a: ["most practical", "less practical", "practicalest"], c: 0 },
        { q: "___ all due respect, I think the figures tell a different story.", a: ["With", "For", "In"], c: 0 },
        { q: "I take your ___, but we also need to consider the cost.", a: ["point", "opinion", "idea"], c: 0 },
        { q: "The proposal is ___ ambitious, given our budget. (несколько)", a: ["somewhat", "some", "somehow"], c: 0 },
        { q: "Would it be possible ___ the meeting to Thursday?", a: ["to move", "moving", "move"], c: 0 }
      ]
    },
    read: {
      title: "Тихое искусство говорить «нет»",
      text: "Ask a retired envoy what the job really involves and you are unlikely to hear about grand summits or signing ceremonies. You are far more likely to hear about language: the endless, painstaking work of finding words that allow two governments to disagree without either of them losing face. One former ambassador, who spent three decades in postings from Cairo to Canberra, put it to me this way: “Diplomacy is the art of telling someone something they would rather not hear, in a way that leaves them grateful you said it.”\n\nThat art has its own grammar. A diplomat rarely says that a proposal is unacceptable; she says it “presents certain difficulties”. A government does not reject an offer outright; it “notes it with interest”. To the uninitiated this can sound evasive, even faintly absurd. Yet the vagueness is deliberate. Every softened phrase leaves the door ajar, and an open door is worth more at the negotiating table than a satisfying slam.\n\nConsider how a stalemate is typically broken. Publicly, both sides may be posturing for domestic audiences, insisting that they will make no concessions whatsoever. Privately, however, a back channel is often already humming. Junior officials, or occasionally a trusted emissary from a neutral country, sound out what each side could tolerate without appearing to back down. The resulting overtures are carefully hedged: a minister “would not rule out” further talks; a spokesperson suggests that recent remarks “may have been misinterpreted”. Each phrase is a small, deniable signal, and each requires a tacit acknowledgement from the other side before anyone risks anything more concrete.\n\nThis is why apparently trivial wording disputes can stall a bilateral accord for months. Whether a text “recognises” or merely “acknowledges” a claim to sovereignty may determine whether a parliament is willing to ratify it at all. Negotiators who seem intransigent over a single adjective are frequently defending a position that would be impossible to explain back home.\n\nNone of this means that diplomacy is merely a matter of polite evasion. Brinkmanship still exists, and some leaders clearly relish it. But even the most confrontational governments tend to rely on conciliatory language once the cameras are off, because a thaw in relations is almost always cheaper than the alternative. The olive branch, in other words, is usually extended in a subordinate clause.\n\nWhat can those of us outside the foreign service learn from this? Perhaps that tact is not the opposite of honesty but a way of making honesty survivable. Saying “I'm not sure this is quite the right moment” rather than “No” does not disguise your meaning; any competent listener will understand you perfectly. What it does is give the other person room to retreat with dignity, and people who are allowed to retreat with dignity are far more likely to return to the table.\n\nThe ambassador, for his part, has one rule he still follows in retirement, even at family dinners. “Never win an argument so completely,” he says, “that the other person has nothing left to lose.”",
      gloss: [["painstaking", "кропотливый"], ["ajar", "приоткрытый"], ["the uninitiated", "непосвящённые"], ["sound out", "прощупать (позицию)"], ["hedged", "сформулированный с оговорками"], ["deniable", "такой, от которого можно откреститься"], ["relish", "наслаждаться, смаковать"]],
      qs: [
        { q: "What is the main point of the article?", a: ["Carefully softened language is a practical tool that keeps negotiations alive", "Diplomats are trained to avoid telling the truth", "Grand summits matter more than private negotiations"], c: 0 },
        { q: "According to the article, why might a parliament refuse to ratify an accord?", a: ["Because of the precise verb used about a sovereignty claim", "Because the back channel was exposed", "Because the envoy offended its members"], c: 0 },
        { q: "What does the writer suggest about public posturing?", a: ["It is often aimed at voters at home while private talks continue", "It usually signals that talks have collapsed", "It is the main way concessions are offered"], c: 0 },
        { q: "What is the writer's attitude to tact?", a: ["It makes honesty easier to accept rather than replacing it", "It is a polite form of dishonesty", "It is useful only in the foreign service"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Tom", "Right, the minister called their trade proposal ‘frankly ridiculous’ on live radio. We need a statement by noon."],
        ["Priya", "Lovely. So we're going from ‘frankly ridiculous’ to what, exactly? ‘Warmly welcomed’?"],
        ["Tom", "Let's not overshoot. I was thinking something like ‘the minister's remarks were not intended to prejudge the outcome of ongoing discussions.’"],
        ["Priya", "Not bad. Though ‘not intended’ implies he said something he didn't mean, which, to be fair, he did."],
        ["Tom", "Well, we can hardly say he meant it. Their ambassador's already asked for a meeting."],
        ["Priya", "Asked or demanded?"],
        ["Tom", "The email said ‘at your earliest convenience’, which in my experience means ‘by lunchtime or else’."],
        ["Priya", "Okay. What if we add that we ‘value the constructive spirit in which the proposal was made’? It lets them save face without us conceding anything on substance."],
        ["Tom", "I like it. And maybe offer a bilateral meeting at official level, not ministerial. Keep it low-key."],
        ["Priya", "Agreed. The last thing we need is a summit where he repeats it in front of the cameras."],
        ["Tom", "Should we mention the word ‘ridiculous’ at all?"],
        ["Priya", "Absolutely not. The statement should read as if nobody had ever heard of radio."],
        ["Tom", "Perfect. I'll draft it, you check the tone, and we pray he doesn't do the evening news."],
        ["Priya", "I've already rung his office. Apparently he's ‘unavailable for comment for the foreseeable future’."]
      ],
      qs: [
        { q: "What problem are Tom and Priya dealing with?", a: ["A minister publicly insulted another country's proposal", "An ambassador has been expelled", "A trade deal collapsed at a summit"], c: 0 },
        { q: "What does Tom imply about the phrase ‘at your earliest convenience’?", a: ["It actually conveys urgency and displeasure", "It means there is no hurry", "It suggests the ambassador is willing to compromise"], c: 0 },
        { q: "Why does Priya suggest praising the ‘constructive spirit’ of the proposal?", a: ["It soothes the other side without changing their own position", "It signals that they will accept the proposal", "It shifts the blame onto the other country"], c: 0 },
        { q: "Why do they prefer an official-level meeting?", a: ["To keep things low-profile and avoid another public gaffe", "Because the minister refuses to attend", "Because the ambassador has requested it"], c: 0 }
      ]
    },
    speak: ["I'm not entirely convinced that this is the right moment to raise the issue, but I'd be happy to discuss it once tensions have eased.", "With all due respect, the proposal presents certain difficulties for us, and we would welcome a little more time to consider it.", "A modest concession on our part now could allow both sides to save face and might eventually pave the way for a lasting accord.", "Rather than issuing a public rebuke, it might be wiser to use a back channel and quietly sound out what they could accept."],
    write: {
      trans: [
        ["Смягчи фразу (не до конца): I'm not ___ sure this will work.", ["entirely", "completely", "totally", "altogether", "quite", "fully"]],
        ["Вставь выражение (сохранить лицо): The compromise allowed both governments to ___.", ["save face"]],
        ["Смягчи просьбу прошедшим длительным (я хотел бы узнать): I ___ whether you could reconsider.", ["was wondering"]],
        ["Перефразируй безлично, используя пассив: You missed the deadline. → It appears that the deadline ___.", ["has been missed", "was missed"]]
      ],
      prompt: "Ты — сотрудник посольства. Напиши официальное письмо представителю другой страны: тактично откажись от их предложения провести крупное совместное мероприятие, сохрани хорошие отношения и предложи альтернативу.",
      minWords: 240, use: ["overture", "bilateral", "concession", "save face"],
      model: "Dear Mr Hallström,\n\nThank you for your letter of 12 March and for the generous overture it contained. We were genuinely pleased to learn that your ministry is considering a joint cultural festival next spring, and we fully share your view that closer bilateral cooperation in this area would benefit both our countries.\n\nHaving discussed the proposal in some detail, however, I am afraid we are not entirely convinced that the timing is right. As you may be aware, our ministry is currently undergoing a major restructuring, and it would be difficult for us to commit the staff and funding that an event of this scale would deserve. We would be most reluctant to agree to a project that we could not support wholeheartedly, as this would hardly do justice to your initiative.\n\nThat said, we would very much like to keep the conversation going. Might I suggest, as an alternative, a smaller series of film screenings in both capitals during the autumn? This would allow our teams to build a working relationship and test the format before considering something more ambitious. We would, of course, be willing to make a concession on the venue and cover the costs of the first screening ourselves.\n\nI hope you will see this not as a refusal, but as an invitation to proceed step by step. A gradual approach would also ensure that, should plans change, neither side is left needing to save face.\n\nI look forward to hearing your thoughts and would be delighted to arrange a call at your convenience.\n\nYours sincerely,\nAnna Volkova\nCultural Attaché"
    }
  },
  {
    t: "Разрешение конфликтов",
    words: [
      ["grievance", "обида, жалоба, претензия", "грИвэнс"], ["rift", "разлад, раскол", "рифт"], ["bone of contention", "яблоко раздора", "боун эв кэнтЭншн"], ["bury the hatchet", "зарыть топор войны", "бЭри зэ хЭчит"], ["clear the air", "разрядить обстановку, объясниться", "клИэ зи Эа"],
      ["common ground", "точки соприкосновения", "кОмэн грАунд"], ["meet halfway", "пойти навстречу, найти компромисс", "мит хафуЭй"], ["arbitration", "арбитраж, третейский суд", "арбитрЭйшн"], ["mediate", "быть посредником, улаживать", "мИдиэйт"], ["impasse", "тупик, безвыходное положение", "Импас"],
      ["defuse", "разрядить (ситуацию)", "дифьЮз"], ["placate", "успокоить, умиротворить", "плэкЭйт"], ["appease", "задобрить, умиротворить уступками", "эпИз"], ["rapport", "взаимопонимание, контакт", "рэпО"], ["reconcile", "примирить", "рЭкэнсайл"],
      ["acrimonious", "ожесточённый, язвительный", "экримОуниэс"], ["animosity", "враждебность", "энимОсити"], ["flare-up", "вспышка (конфликта, гнева)", "флЭэр-ап"], ["simmer", "назревать, тлеть", "сИмэ"], ["sore point", "больное место", "со пойнт"],
      ["vent", "выплеснуть (эмоции)", "вэнт"], ["backpedal", "идти на попятную", "бэкпЭдл"], ["climb down", "уступить, отступить от позиции", "клайм дАун"], ["rancour", "озлобленность, злоба", "рЭнкэ"], ["amicable", "дружелюбный, мирный", "Эмикэбл"],
      ["concede", "признать, уступить", "кэнсИд"], ["smooth things over", "сгладить ситуацию", "смуз сингз Оувэ"], ["at loggerheads", "в ссоре, на ножах", "эт лОгэхэдз"], ["sticking point", "камень преткновения", "стИкинг пойнт"], ["de-escalate", "снизить напряжённость", "ди-Эскэлэйт"]
    ],
    phrases: [["Can we try to look at this from both sides?", "Давайте попробуем взглянуть на это с обеих сторон."], ["I can see where you're coming from.", "Я понимаю, почему вы так думаете."], ["Let's focus on what we can agree on.", "Давайте сосредоточимся на том, в чём мы согласны."], ["I didn't mean to come across as dismissive.", "Я не хотел показаться пренебрежительным."], ["Is there any room for compromise here?", "Здесь есть место для компромисса?"], ["Let's agree to disagree on that point.", "Давайте останемся каждый при своём мнении по этому вопросу."]],
    grammar: {
      title: "Смягчение и вежливость",
      text: "Смягчение (hedging) делает высказывание менее категоричным и оставляет собеседнику пространство для ответа. Основные средства: модальные глаголы might, could, would (This could be a problem вместо This is a problem); глаголы seem, appear, tend to (It seems there's been a misunderstanding); вводные perhaps, possibly, arguably; уменьшение масштаба — a bit, slightly, a little (I'm a little concerned). Вежливые просьбы: Would you mind + -ing, Do you think you could...?, а также отрицательная просьба с хвостиком: You couldn't send it again, could you? В конфликте особенно важно говорить о своём восприятии, а не обвинять: I feel that..., From my perspective... вместо You always.... Типичная ошибка русскоязычных — Would you mind to help? Правильно: Would you mind helping? Ещё одна — слишком прямое «You must» в просьбах; must звучит как приказ, мягче You might want to... или It might be worth... Помните: на вопрос Would you mind...? ответ «No, not at all» означает согласие.",
      examples: [["It seems there may have been a slight misunderstanding.", "Похоже, возникло небольшое недопонимание."], ["Would you mind explaining what you meant by that?", "Не могли бы вы объяснить, что вы имели в виду?"], ["You might want to check the figures again before the meeting.", "Возможно, стоит ещё раз проверить цифры перед встречей."], ["From my perspective, the issue is more about communication than workload.", "С моей точки зрения, дело скорее в общении, чем в нагрузке."], ["You couldn't give me a hand with this, could you?", "Ты не мог бы мне с этим помочь?"]],
      quiz: [
        { q: "Would you mind ___ the window?", a: ["closing", "to close", "close"], c: 0 },
        { q: "It ___ that there has been a misunderstanding.", a: ["seems", "is seeming", "seemed to"], c: 0 },
        { q: "You ___ want to double-check the contract before signing. (возможно, стоит)", a: ["might", "must", "should to"], c: 0 },
        { q: "I'm ___ concerned about the delays. (немного)", a: ["a little", "a few", "little bit"], c: 0 },
        { q: "You couldn't lend me your notes, ___?", a: ["could you", "couldn't you", "can't you"], c: 0 },
        { q: "From my ___, the problem is the lack of clear roles.", a: ["perspective", "opinion side", "look"], c: 0 },
        { q: "Do you think you ___ send me the updated version?", a: ["could", "can to", "would to"], c: 0 },
        { q: "Would you mind if I ___ a suggestion?", a: ["made", "make to", "will make"], c: 0 }
      ]
    },
    read: {
      title: "В комнате медиатора",
      text: "People tend to imagine that my job begins with shouting. In fact, by the time I am called in, the shouting has usually stopped. What remains is something quieter and far harder to shift: two colleagues who have been at loggerheads for so long that they no longer remember quite how it started, only that the other person is to blame.\n\nTake a case from last spring. Two senior engineers, whom I will call Maya and Daniel, had once been close collaborators. A disagreement over credit for a successful project had turned into a rift, and the rift had hardened into open animosity. Their manager had tried to smooth things over twice; both attempts ended in a flare-up that the whole open-plan office could hear. By the time I arrived, the team had split into factions and productivity had collapsed.\n\nMy first task in any dispute is not to resolve it but to listen. I meet each party separately and let them vent, sometimes for an hour or more. This can seem self-indulgent, but grievances that have been simmering for months need somewhere to go. More importantly, these sessions allow me to build rapport, and without trust neither party will believe that I am genuinely impartial.\n\nIt soon became clear that the bone of contention was not really the project at all. Daniel felt that Maya had presented their joint work to the board as her own; Maya felt that Daniel had been dismissive of her ideas for years and that the presentation was the first time she had been properly heard. Each of them was right, at least in part, which is precisely why the conflict had reached an impasse.\n\nWhen I finally brought them into the same room, the atmosphere was acrimonious. Daniel opened by listing every slight he could remember. Maya began to backpedal on points she had made forcefully in private, which only made him angrier. It was at this point that I asked them both to stop and describe, without using the word “you”, what they actually needed in order to work together. That small change defused the tension remarkably quickly. Once they could not accuse, they had to explain.\n\nWhat emerged was more common ground than either had expected. Both wanted public acknowledgement of their contribution; both wanted a clearer division of responsibilities. The sticking point was the past: Daniel wanted an apology, and Maya regarded apologising as a humiliating climb-down. We eventually agreed on a jointly written note to the board crediting the whole team, which allowed each of them to meet the other halfway without anyone having to concede defeat.\n\nI would love to report that they buried the hatchet and became friends again. They did not. But their relationship is now amicable and professional, and that, in my experience, is a perfectly respectable outcome. Reconciling people does not mean making the rancour disappear overnight. It means clearing the air enough for them to get on with their work, while respecting the sore points that may never quite heal.",
      gloss: [["self-indulgent", "потакающий своим слабостям"], ["impartial", "беспристрастный"], ["faction", "группировка, фракция"], ["slight", "обида, проявление неуважения"], ["dismissive", "пренебрежительный"], ["concede defeat", "признать поражение"]],
      qs: [
        { q: "Why does the mediator let each party vent before any joint meeting?", a: ["To release pent-up frustration and earn their trust", "To collect evidence of who was to blame", "To persuade them to accept a solution quickly"], c: 0 },
        { q: "What does the writer identify as the real cause of the conflict?", a: ["Long-standing feelings of not being valued or credited", "A technical disagreement about the project", "Pressure from the board to deliver results"], c: 0 },
        { q: "Why did the instruction not to use the word “you” work?", a: ["It forced them to explain their needs instead of making accusations", "It made the conversation more formal and distant", "It stopped Daniel from talking altogether"], c: 0 },
        { q: "How does the writer feel about the final outcome?", a: ["Realistically satisfied, even though no friendship was restored", "Disappointed that the two did not reconcile fully", "Surprised that the board accepted the note"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Hannah", "Okay, so I thought it might be good to clear the air before this turns into a full-blown cold war."],
        ["Leo", "Is this about the washing-up? Because I did a pan on Tuesday."],
        ["Sam", "A pan. Singular. There's currently a lasagne dish in the sink that's developing its own ecosystem."],
        ["Hannah", "Sam, maybe let's not open with sarcasm. Leo, it's not just the dishes. It's more that we seem to have slightly different ideas about what ‘clean’ means."],
        ["Leo", "Fair enough. Though I'd gently point out that someone's been practising the drums at one in the morning."],
        ["Sam", "That was once. And it was an electronic kit with headphones."],
        ["Leo", "Headphones don't muffle the actual thumping, mate. My ceiling's basically a drum skin."],
        ["Hannah", "Right, so we've got two sore points. Could we maybe try meeting halfway on both?"],
        ["Sam", "Go on then. What are you proposing, oh wise mediator?"],
        ["Hannah", "A cleaning rota we actually stick to, and no drumming after eleven. Would anyone be willing to try that for a month?"],
        ["Leo", "I could live with that. I'd also be happy to deal with the lasagne dish, as a gesture of goodwill."],
        ["Sam", "Wow. Okay, then I'll buy one of those mats that cuts down the vibration. Peace offering."],
        ["Hannah", "Look at us. Burying the hatchet before it's even been properly sharpened."],
        ["Leo", "Let's not get carried away. Ask me again after the first week of the rota."]
      ],
      qs: [
        { q: "Why does Hannah start the conversation?", a: ["To deal with tensions before they get worse", "Because the landlord has complained", "Because Leo wants to move out"], c: 0 },
        { q: "What does Sam's comment about the ‘ecosystem’ imply?", a: ["The dish has been left unwashed for a long time", "The kitchen is full of plants", "Leo is a very keen cook"], c: 0 },
        { q: "What is Leo's complaint about the drumming?", a: ["The vibrations still come through despite the headphones", "Sam plays the drums every night", "The drum kit is too expensive"], c: 0 },
        { q: "How does Leo feel about the agreement at the end?", a: ["Cautiously optimistic but wants to see if it lasts", "Completely convinced it will solve everything", "Unhappy because he gave up too much"], c: 0 }
      ]
    },
    speak: ["I wonder if it might help to clear the air first, so that we can focus on the issues rather than on who said what.", "From my perspective, the sticking point isn't the budget itself but the way the decision was communicated to the team.", "Would you mind if we took a short break? I think we could all do with a moment to reflect before continuing.", "It seems we have more common ground than we thought, so perhaps we could each meet the other halfway on the remaining points."],
    write: {
      trans: [
        ["Вставь глагол в правильной форме (помочь): Would you mind ___ me with this report?", ["helping"]],
        ["Смягчи категоричность (похоже): It ___ there has been a misunderstanding.", ["seems", "appears", "would seem", "would appear"]],
        ["Вставь идиому (зарыли топор войны): After years of feuding, the brothers finally ___.", ["buried the hatchet"]],
        ["Добавь разделительный вопрос: You couldn't send me the file again, ___?", ["could you"]]
      ],
      prompt: "Ты руководитель команды. Двое твоих сотрудников конфликтуют из-за распределения обязанностей. Напиши им общее письмо: признай проблему, тактично опиши ситуацию без обвинений и предложи конкретный план её решения.",
      minWords: 240, use: ["clear the air", "common ground", "would you mind", "meet halfway"],
      model: "Dear Olga and Mark,\n\nI wanted to write to you both before our meeting on Thursday, as I think it would be helpful to clear the air and agree on a way forward.\n\nIt seems to me that the recent tension has less to do with either of you personally and more to do with how responsibilities on the Henderson account were divided in the first place. That was, to a large extent, my oversight, and I apologise for not addressing it sooner. When roles are unclear, it is perfectly natural for people to feel that they are carrying more than their fair share, and I suspect that is how you have both been feeling.\n\nFrom what each of you has told me, there is actually a good deal of common ground. You both want the client to be happy, you both want clearer deadlines, and you both want your work to be recognised. Where you differ is mainly over who should handle client communication, and I believe that is a problem we can solve.\n\nWhat I would like to propose is this. Before Thursday, would you mind each writing down the three tasks you feel most suited to and the three you would rather hand over? We can then compare the lists together and, where they overlap, try to meet halfway. I would also suggest a short weekly check-in for the next month, so that small frustrations do not have a chance to build up.\n\nI know the past few weeks have not been easy, and I genuinely appreciate the professionalism you have both shown. I am confident we can find an arrangement that works for everyone.\n\nBest regards,\nElena"
    }
  },
  {
    t: "Публичные выступления",
    words: [
      ["rhetoric", "риторика", "рЭтэрик"], ["oratory", "ораторское искусство", "Орэтэри"], ["orator", "оратор", "Орэтэ"], ["eloquence", "красноречие", "Элэквэнс"], ["podium", "трибуна, подиум", "пОудиэм"],
      ["lectern", "кафедра, пюпитр для выступающего", "лЭктэн"], ["heckle", "перебивать выкриками", "хЭкл"], ["stage fright", "страх сцены", "стэйдж фрайт"], ["ad-lib", "импровизировать", "эд-лИб"], ["cue cards", "карточки-подсказки", "кью кадз"],
      ["soundbite", "яркая короткая цитата", "сАундбайт"], ["captivate", "пленять, захватывать внимание", "кЭптивэйт"], ["enthral", "очаровывать, завораживать", "инсрОл"], ["resonate", "находить отклик", "рЭзэнэйт"], ["pause for effect", "выдержать паузу для эффекта", "поз фэр ифЭкт"],
      ["rhetorical question", "риторический вопрос", "ритОрикэл квЭсчэн"], ["punchline", "кульминация шутки, «соль»", "пАнчлайн"], ["rapt", "поглощённый, захваченный", "рэпт"], ["filler words", "слова-паразиты", "фИлэ уёдз"], ["gesticulate", "жестикулировать", "джэстИкьюлэйт"],
      ["hold the floor", "держать слово, удерживать внимание", "хоулд зэ фло"], ["win over", "склонить на свою сторону", "уин Оувэ"], ["bombastic", "напыщенный", "бомбЭстик"], ["pithy", "сжатый и ёмкий", "пИси"], ["peroration", "заключительная часть речи", "пэрэрЭйшн"],
      ["call to action", "призыв к действию", "кол ту Экшн"], ["tongue-tied", "лишившийся дара речи, косноязычный", "тАн-тайд"], ["keynote", "основной доклад", "кИноут"], ["rabble-rousing", "подстрекательский, демагогический", "рЭбл-раузинг"], ["off the cuff", "экспромтом, без подготовки", "оф зэ каф"]
    ],
    phrases: [["Let me start with a question.", "Позвольте начать с вопроса."], ["Bear with me for a moment.", "Потерпите минутку."], ["That brings me to my next point.", "Это подводит меня к следующему пункту."], ["I'd like to leave you with one final thought.", "Хочу оставить вас с одной последней мыслью."], ["Imagine, for a moment, a city without traffic.", "Представьте на мгновение город без пробок."], ["Thank you for your attention; I'm happy to take questions.", "Спасибо за внимание, я готов ответить на вопросы."]],
    grammar: {
      title: "Приёмы убеждения",
      text: "Убедительная речь опирается не только на аргументы, но и на построение фраз. Правило трёх: перечисление из трёх элементов звучит завершённо и запоминается (We will learn, we will adapt, and we will succeed). Риторический вопрос вовлекает слушателей: Can we really afford to wait another decade? Антитеза противопоставляет понятия: It is not a cost; it is an investment. Анафора — повтор начала фраз: Every child..., every family..., every community.... Расщеплённые предложения (cleft sentences) выделяют главное: What we need is courage. It was the volunteers who made this possible. Инверсия после отрицательных и ограничительных наречий добавляет драматизма: Never before have we had such an opportunity. Not only does it save money, but it also saves lives. Only by working together can we succeed. Эмфатическое do усиливает утверждение: We do care about your concerns. Инклюзивное we создаёт общность со слушателями. Типичная ошибка русскоязычных — забыть вспомогательный глагол при инверсии: Never before we have seen... — неверно, нужно Never before have we seen....",
      examples: [["Never before have we had such a clear opportunity to change things.", "Никогда прежде у нас не было такой явной возможности всё изменить."], ["What this city needs is not more promises but real action.", "Этому городу нужны не новые обещания, а реальные действия."], ["Not only does the plan reduce costs, but it also improves safety.", "План не только снижает расходы, но и повышает безопасность."], ["It was the volunteers who made this festival possible.", "Именно волонтёры сделали этот фестиваль возможным."], ["We do understand your concerns, and we will address them.", "Мы действительно понимаем ваши опасения и учтём их."]],
      quiz: [
        { q: "Never before ___ such a turnout at a local election.", a: ["have we seen", "we have seen", "we saw"], c: 0 },
        { q: "___ we need now is courage, not caution.", a: ["What", "That", "Which"], c: 0 },
        { q: "Not only ___ save money, but it also saves time.", a: ["does it", "it does", "it"], c: 0 },
        { q: "It was the nurses ___ kept the hospital running.", a: ["who", "what", "which they"], c: 0 },
        { q: "We ___ care about your opinion. (эмфатическое усиление)", a: ["do", "are", "does"], c: 0 },
        { q: "Can we really afford ___ another decade?", a: ["to wait", "waiting for", "wait"], c: 0 },
        { q: "Rarely ___ a speaker held an audience so completely.", a: ["has", "have", "is"], c: 0 },
        { q: "Only by working together ___ overcome this crisis.", a: ["can we", "we can", "we will"], c: 0 }
      ]
    },
    read: {
      title: "Почему лучшие речи звучат как разговор",
      text: "I have written speeches for politicians, chief executives and, on one memorable occasion, a best man who was so tongue-tied with stage fright that he read my words off his cue cards without once looking up. Over fifteen years, I have come to one slightly unfashionable conclusion: the speeches that truly captivate an audience are rarely the ones packed with the most dazzling rhetoric.\n\nWe tend to associate oratory with grand gestures: the leader at the podium, gesticulating wildly, delivering line after line of soaring prose. And there is a place for that. Some of history's most celebrated orators could enthral a crowd of thousands with sheer eloquence. But eloquence is not the same as volume, and much of what passes for powerful speaking today is merely bombastic. An audience can tell the difference between someone who is speaking to them and someone who is performing at them.\n\nThe best speakers I have worked with do something deceptively simple. They talk as though they were addressing one intelligent friend across a table. Their sentences are short. Their examples are concrete. Their jokes, when they come, arrive naturally rather than being bolted on to a speech that has no need of a punchline. And crucially, they are not afraid of silence. A well-judged pause for effect after a key sentence does more than any adjective to signal that something matters.\n\nThis is not to say that structure is unimportant. Quite the opposite. The rule of three, the rhetorical question, the carefully balanced contrast: these techniques have survived since antiquity precisely because they work. A pithy line that resonates with the audience's own experience will be remembered long after the statistics have faded. The trick is to use these devices so naturally that no one notices them. The moment listeners can see the machinery, they stop trusting the message.\n\nThen there is the question of delivery. I always tell nervous speakers to cut their filler words ruthlessly in rehearsal, but not to panic if a few slip through on the day. A speaker who occasionally says “um” but clearly believes what they are saying will win over a room far more readily than a flawless reader of an autocue. Likewise, the ability to ad-lib, to respond to a heckle with good humour or to acknowledge a baby crying at the back, often earns more goodwill than the prepared text itself. It shows the audience that a real person is standing behind the lectern.\n\nFinally, every speech needs an ending that earns its place. The classical peroration was meant to sum up the argument and stir the emotions, and that remains good advice. But the most effective endings I have heard are also practical: a clear call to action that tells listeners exactly what they can do next. If people leave the hall moved but uncertain, the speech has only half worked.\n\nSo, if you are preparing to hold the floor at a conference or a wedding, by all means polish your soundbites. But spend just as much time imagining the faces in front of you. An audience held rapt is rarely an audience that has been lectured; it is one that feels it has been spoken to.",
      gloss: [["unfashionable", "немодный, непопулярный"], ["soaring prose", "возвышенная, патетичная речь"], ["bolted on", "приделанный искусственно"], ["antiquity", "античность"], ["autocue", "телесуфлёр"], ["the machinery", "механизм, «кухня»"], ["stir the emotions", "взволновать"]],
      qs: [
        { q: "What is the writer's central argument?", a: ["Speeches work best when they feel natural and personal rather than showy", "Rhetorical techniques are outdated and should be avoided", "Only experienced orators can captivate large audiences"], c: 0 },
        { q: "What does the writer say about rhetorical devices?", a: ["They are effective as long as the audience does not notice them", "They only work in political speeches", "They distract from the speaker's personality"], c: 0 },
        { q: "Why might a speaker who says “um” be more persuasive than a flawless reader?", a: ["Because sincerity matters more to listeners than technical perfection", "Because filler words make a speech sound longer", "Because audiences dislike speakers who rehearse"], c: 0 },
        { q: "What does the writer believe a good ending should include?", a: ["A concrete suggestion of what listeners should do next", "A final joke to leave people smiling", "A detailed summary of all the statistics"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Ruth", "Okay, Ben, from the top. And this time, try not to apologise for existing before you've even said hello."],
        ["Ben", "I don't apologise. I just say, ‘Sorry, I'll keep this brief.’"],
        ["Ruth", "Which tells three hundred people you'd rather be anywhere else. Open with the story about your grandfather's workshop instead."],
        ["Ben", "Isn't that a bit sentimental for a logistics conference?"],
        ["Ruth", "It's the only part of the speech where you actually sound like a human being. Trust me, it'll resonate."],
        ["Ben", "Fine. And then I go straight into the figures on delivery times?"],
        ["Ruth", "Not straight in. Ask them a question first. Something like, ‘How many of you have waited in all day for a parcel that never came?’"],
        ["Ben", "Every single one of them, presumably. They work in logistics."],
        ["Ruth", "Exactly. Instant laugh, instant connection. Then you hit them with the numbers."],
        ["Ben", "What about my slide with the forty-seven bullet points?"],
        ["Ruth", "I've taken the liberty of deleting it. What remains is three points, one image and a very long pause."],
        ["Ben", "A pause? What do I do during the pause?"],
        ["Ruth", "Nothing. That's the point. You stand there, you look at them, and you let the silence do the work."],
        ["Ben", "Right. So my big strategy for the keynote is to stop talking."],
        ["Ruth", "Occasionally, yes. You'd be amazed how many speakers never discover it."]
      ],
      qs: [
        { q: "What habit does Ruth want Ben to drop?", a: ["Starting his speech with an apology", "Speaking too quickly", "Reading from his notes"], c: 0 },
        { q: "Why does Ruth want him to tell the story about his grandfather?", a: ["It makes him sound genuine and relatable", "It is closely linked to delivery statistics", "The organisers specifically requested it"], c: 0 },
        { q: "Why does Ben think the question about parcels has an obvious answer?", a: ["Because everyone in the audience works in the delivery business", "Because he asked it in a previous talk", "Because parcels rarely go missing"], c: 0 },
        { q: "What has Ruth done to his slides?", a: ["Cut them down drastically to the essentials", "Added more bullet points and images", "Replaced them with a video"], c: 0 }
      ]
    },
    speak: ["Never before have we had the tools, the knowledge and the resources to tackle this problem so effectively, so why are we still hesitating?", "What our community needs is not another report gathering dust on a shelf, but a clear plan that people can actually see working.", "Not only does this proposal reduce costs in the long term, but it also gives young people a genuine reason to stay in the town.", "I would urge every one of you to leave this hall tonight not simply inspired, but ready to take one concrete step towards change."],
    write: {
      trans: [
        ["Используй инверсию (никогда прежде): We have never seen such enthusiasm. → Never before ___ such enthusiasm.", ["have we seen"]],
        ["Перефразируй с выделением (What): We need more time. → ___ is more time.", ["What we need"]],
        ["Используй инверсию (не только): It not only saves money but also time. → Not only ___ money, but it also saves time.", ["does it save"]],
        ["Выдели подлежащее (It was ... who): The volunteers saved the festival. → ___ who saved the festival.", ["It was the volunteers"]]
      ],
      prompt: "Напиши текст выступления на городском собрании: убеди жителей поддержать проект по превращению заброшенного завода в общественный центр. Используй приёмы убеждения: риторический вопрос, правило трёх, инверсию и призыв к действию.",
      minWords: 260, use: ["never before", "what we need", "not only", "resonate"],
      model: "Good evening, everyone, and thank you for coming out on such a cold night.\n\nTen years ago, the old textile factory employed nearly a thousand people from this town. Today, its windows are broken, its gates are chained, and its walls are covered in graffiti. Every one of us walks past it. And every one of us, I suspect, has wondered whether anything could ever be done with it.\n\nTonight, I want to tell you that something can.\n\nOur proposal is simple. We want to turn the old factory into a community centre: a place for young people to study, for older residents to meet, and for local businesses to start and grow. Not only would this give new life to a building that has stood empty for a decade, but it would also bring jobs, visitors and investment back to the heart of our town.\n\nSome people will say it is too expensive. But let me ask you this: how much is it costing us to do nothing? How many young people have already left because there is nowhere for them to go? How many shops on Market Street have closed their doors for good?\n\nNever before have we had such an opportunity. The regional fund has agreed to cover sixty per cent of the costs, provided that we can show genuine local support. What we need now is not money from your pockets, but your voices, your ideas and your signatures.\n\nI hope this vision will resonate with you as strongly as it does with me. So, on your way out tonight, please sign the petition by the door, tell your neighbours, and come to the planning meeting next Tuesday. Together, we can turn a symbol of decline into a symbol of hope.\n\nThank you."
    }
  },
  {
    t: "Интервью",
    words: [
      ["interviewee", "интервьюируемый, кандидат на собеседовании", "интэвьюИ"], ["probing question", "глубокий, «зондирующий» вопрос", "прОубинг квЭсчэн"], ["curveball", "каверзный, неожиданный вопрос", "кЁвбол"], ["evasive", "уклончивый", "ивЭйсив"], ["sidestep", "уходить (от вопроса)", "сАйдстэп"],
      ["off the record", "не для печати, неофициально", "оф зэ рЭкод"], ["candid", "откровенный", "кЭндид"], ["forthcoming", "открытый, охотно делящийся информацией", "фоскАминг"], ["put someone on the spot", "поставить в неловкое положение", "пут сАмуан он зэ спот"], ["grill", "допрашивать с пристрастием", "грил"],
      ["elaborate", "подробно развить (мысль)", "илЭбэрэйт"], ["track record", "послужной список, опыт достижений", "трэк рЭкод"], ["transferable skills", "универсальные навыки", "трэнсфЁрэбл скилз"], ["headhunt", "переманивать (специалиста)", "хЭдхант"], ["panel interview", "собеседование с комиссией", "пЭнл Интэвью"],
      ["competency-based", "основанный на компетенциях", "кОмпитэнси-бэйст"], ["remuneration", "вознаграждение, оплата труда", "римьюнэрЭйшн"], ["negotiable", "подлежащий обсуждению", "нигОушиэбл"], ["undersell oneself", "недооценивать себя, принижать свои достоинства", "андэсЭл уансЭлф"], ["overqualified", "со слишком высокой квалификацией", "оувэквОлифайд"],
      ["tease out", "выведать, вытянуть (информацию)", "тиз Аут"], ["verbatim", "дословно", "вэбЭйтим"], ["transcript", "стенограмма, расшифровка", "трЭнскрипт"], ["follow-up question", "уточняющий вопрос", "фОлоу-ап квЭсчэн"], ["loaded question", "вопрос с подвохом", "лОудид квЭсчэн"],
      ["rehearsed", "отрепетированный", "рихЁст"], ["poise", "самообладание, уверенность", "пойз"], ["composure", "спокойствие, выдержка", "кэмпОужэ"], ["come across as", "производить впечатление (кого-то)", "кам экрОс эз"], ["point-blank", "напрямую, в упор", "пойнт-блЭнк"]
    ],
    phrases: [["That's a very good question.", "Это очень хороший вопрос."], ["Could I just clarify what you mean by that?", "Можно уточнить, что вы под этим подразумеваете?"], ["Let me give you a concrete example.", "Позвольте привести конкретный пример."], ["I'd rather not comment on that at this stage.", "На данном этапе я бы предпочёл это не комментировать."], ["What would a typical day in this role look like?", "Как выглядит типичный день на этой должности?"], ["Thank you for taking the time to meet with me.", "Спасибо, что нашли время встретиться со мной."]],
    grammar: {
      title: "Шкала формальности",
      text: "В английском один и тот же смысл можно выразить на разных уровнях формальности, и умение выбрать нужный уровень — часть профессиональной компетенции. Формальный регистр использует слова латинского происхождения (obtain, commence, inquire, assist), полные формы без сокращений, пассив и безличные конструкции (It has been decided that...), инверсию с should (Should you require...). Нейтральный — обычная деловая речь: get, start, ask, help. Неформальный — фразовые глаголы, сокращения, разговорные слова (sort out, figure out, kind of, stuff). Сравните: «We regret to inform you that your application has been unsuccessful» (официальное письмо), «Unfortunately, we won't be taking your application further» (нейтрально), «Sorry, you didn't get it» (разговор с другом). На собеседовании держитесь нейтрально-формального уровня: «I'd welcome the opportunity to...», но без канцелярита. Русскоязычные часто впадают в крайности: звучат как официальный документ («I would like to inform you that I am a hard-working person») или используют сленг из сериалов. В письме незнакомому работодателю не пишите «Hi guys».",
      examples: [["We would be grateful if you could confirm your availability.", "Мы будем признательны, если вы подтвердите, когда вам удобно."], ["Could you let me know when you're free?", "Можешь сообщить, когда ты свободен?"], ["The meeting will commence at nine o'clock sharp.", "Совещание начнётся ровно в девять."], ["I'd welcome the opportunity to discuss my experience in more detail.", "Я был бы рад возможности подробнее рассказать о своём опыте."], ["We need to sort out the schedule before Friday.", "Нам нужно разобраться с графиком до пятницы."]],
      quiz: [
        { q: "Formal: We regret to ___ you that the position has been filled.", a: ["inform", "tell to", "say"], c: 0 },
        { q: "Formal: Please do not hesitate to ___ us should you need further information.", a: ["contact", "contacting", "contacted"], c: 0 },
        { q: "Formal: The ceremony will ___ at 10 a.m. (начнётся)", a: ["commence", "kick off", "get going"], c: 0 },
        { q: "Informal: Don't worry, we'll ___ it out tomorrow. (разберёмся)", a: ["sort", "solve", "arrange"], c: 0 },
        { q: "Formal: ___ you require any assistance, please contact reception.", a: ["Should", "Would", "Had"], c: 0 },
        { q: "Formal: I would ___ the opportunity to discuss this further. (был бы рад)", a: ["welcome", "love to", "enjoy to"], c: 0 },
        { q: "Formal: Your application ___ carefully considered by the committee.", a: ["has been", "has", "is been"], c: 0 },
        { q: "Formal: We would be grateful if you ___ confirm your attendance.", a: ["could", "can to", "will"], c: 0 }
      ]
    },
    read: {
      title: "Искусство неотрепетированного ответа",
      text: "For almost thirty years, Margaret Okafor has been one of the most feared and, among her peers, most admired interviewers on British radio. Politicians have walked out of her studio; at least one chief executive resigned within a week of appearing on her programme. Yet when I meet her in a quiet café near the broadcasting centre, she is softly spoken, amused and, it soon emerges, faintly suspicious of her own reputation.\n\n“People think I grill my guests,” she says. “I don't, really. I just ask the follow-up question. Most interviewers ask something tough, get an evasive answer and move on to the next topic on their list. I simply ask the same question again, a little more precisely. You'd be astonished how rarely anyone does that.”\n\nShe is dismissive of what she calls “gotcha journalism”: loaded questions designed to trap an interviewee into saying something embarrassing. “It makes good radio for about thirty seconds. But it tells the listener nothing. My job is to tease out what someone actually thinks, not to catch them out.”\n\nHer preparation is famously meticulous. Before a major interview she reads every transcript she can find of her guest's previous appearances, noting the phrases they repeat verbatim. “Those are the rehearsed answers,” she explains. “When I hear one coming, I know I need to ask the question from a different angle, or the guest will simply sidestep it.” Occasionally she throws in a curveball, but only, she insists, when it is relevant. “A surprise question isn't clever in itself. It's clever if it reveals something the rehearsed answers were hiding.”\n\nWhat, I ask, makes a good interviewee? Her answer surprises me. “Not the most polished ones. The guests who come across as most credible are often those who say, ‘That's a fair question, and I don't have a complete answer.’ Listeners can hear candour. They can also hear when someone has been coached to within an inch of their life.”\n\nComposure matters too, she concedes, though not in the way media trainers suggest. “Poise isn't about never hesitating. It's about not panicking when you're put on the spot. The guests who get into real trouble are the ones who feel they must say something, anything, rather than admit they need a moment to think.”\n\nDid she ever feel she had gone too far? She pauses. There was one interview, she admits, early in her career, when she asked a grieving minister a point-blank question about his son. “It was legitimate, technically. But I hadn't earned the right to ask it. I've never forgotten his face.” Since then, she says, she has made a point of building some trust before asking her most probing questions, and of being clear about what is on the record and what is not.\n\nHas anyone ever been more forthcoming off the record? She laughs. “Everyone is. That's rather the problem.” And with that, she declines to elaborate.",
      gloss: [["it emerges", "выясняется"], ["gotcha journalism", "журналистика «ловли на слове»"], ["catch someone out", "подловить кого-то"], ["meticulous", "скрупулёзный"], ["candour", "откровенность, искренность"], ["coached to within an inch of their life", "натасканный до предела"], ["grieving", "скорбящий"]],
      qs: [
        { q: "What does Okafor consider her main technique?", a: ["Repeating a question more precisely when the answer is evasive", "Surprising guests with personal questions", "Preparing a long list of tough topics"], c: 0 },
        { q: "Why does she study transcripts of previous interviews?", a: ["To recognise stock answers so she can approach topics differently", "To find quotations to use against her guests", "To decide which guests to avoid"], c: 0 },
        { q: "According to Okafor, what makes an interviewee credible?", a: ["Admitting the limits of their knowledge honestly", "Answering every question without hesitation", "Sounding as polished as possible"], c: 0 },
        { q: "What does the anecdote about the grieving minister show?", a: ["She learned that a legitimate question can still be ill-judged", "She regrets becoming an interviewer", "She believes personal questions should never be asked"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Jess", "Okay, I'm the interviewer now. ‘So, Dmitri, tell me about yourself.’"],
        ["Dmitri", "Well, I am a very hard-working and responsible person with a strong desire to grow."],
        ["Jess", "Stop. You sound like a cover letter from 2009. Say it the way you'd say it to a colleague you respect."],
        ["Dmitri", "Okay... ‘I've spent the last six years in supply chain analytics, mostly helping retailers cut waste.’"],
        ["Jess", "Much better. Concrete, confident, and nobody's eyes glazed over. Next: ‘What's your biggest weakness?’"],
        ["Dmitri", "Can I say perfectionism?"],
        ["Jess", "You can, if you'd like the panel to roll their eyes in unison. Every second candidate says that."],
        ["Dmitri", "Fine. Honestly, I used to struggle with delegating. I'd rather do things myself than explain them."],
        ["Jess", "Good. And then?"],
        ["Dmitri", "And then I started running short handover sessions, which forced me to trust the team. It's still a work in progress, but it's improved a lot."],
        ["Jess", "That's a proper answer. Now, a curveball: ‘Why should we hire you rather than someone local?’"],
        ["Dmitri", "Er... because I'm cheaper?"],
        ["Jess", "Dmitri."],
        ["Dmitri", "Sorry. Because I've worked across three markets, so I can spot problems that people who've only seen one system tend to miss."],
        ["Jess", "There you go. Just skip the bit where you undersell yourself first."]
      ],
      qs: [
        { q: "What is wrong with Dmitri's first answer?", a: ["It sounds stiff, generic and overly formal", "It is too informal and full of slang", "It is far too long and detailed"], c: 0 },
        { q: "Why does Jess advise against mentioning perfectionism?", a: ["It is a cliché that interviewers hear constantly", "It suggests he cannot meet deadlines", "It is a strength, not a weakness"], c: 0 },
        { q: "What makes his answer about delegating effective?", a: ["He admits a real weakness and shows what he has done about it", "He claims he no longer has any weaknesses", "He blames his previous team for the problem"], c: 0 },
        { q: "What does Jess mean by her final comment?", a: ["He should present his strengths without first putting himself down", "He should talk less about his international experience", "He should ask for a lower salary"], c: 0 }
      ]
    },
    speak: ["I would welcome the opportunity to elaborate on how my experience in international logistics could add value to your team.", "That's a fair question, and while I don't have a complete answer yet, I can tell you how I would approach the problem.", "Should you require any further information regarding my qualifications, please do not hesitate to contact me at your convenience.", "Looking back, I think I came across as rather rehearsed in my first interviews, so now I try to answer more candidly and naturally."],
    write: {
      trans: [
        ["Замени на формальный вариант (начнётся): The interview will start at ten. → The interview will ___ at ten.", ["commence"]],
        ["Замени на формальный вариант (получить): Where can I get a visa? → Where can I ___ a visa?", ["obtain"]],
        ["Перефразируй формально с инверсией (Should): If you need help, contact us. → ___ assistance, please contact us.", ["Should you require", "Should you need"]],
        ["Вставь неформальный фразовый глагол (разобраться с): Don't worry, we'll ___ the problem tomorrow.", ["sort out", "figure out", "work out"]]
      ],
      prompt: "Напиши сопроводительное письмо на должность руководителя проектов в международной компании. Соблюдай нейтрально-формальный регистр: без канцелярита и без разговорных выражений. Расскажи о своём опыте, достижениях и мотивации.",
      minWords: 250, use: ["track record", "transferable skills", "I would welcome", "should you"],
      model: "Dear Ms Patel,\n\nI am writing to apply for the position of Project Manager at Northbridge Consulting, as advertised on your website. Having followed your company's work in sustainable infrastructure for several years, I was particularly pleased to see that you are expanding your team in Central Europe.\n\nFor the past seven years, I have managed logistics and IT projects for a regional distribution company in Kazan, most recently leading a team of twelve specialists across three cities. During that time, I have built a solid track record of delivering complex projects on time and within budget. Last year, for example, I oversaw the introduction of a new warehouse management system that reduced order-processing times by almost a third while keeping costs eight per cent below the original estimate.\n\nAlthough my background is in logistics rather than consulting, I believe that many of my transferable skills would be directly relevant to this role. I am used to coordinating teams with very different priorities, negotiating with suppliers and presenting results clearly to senior management. I also work comfortably in English and Russian and have a good working knowledge of German.\n\nWhat attracts me most to Northbridge is your emphasis on long-term partnerships with clients rather than one-off projects. I am keen to work in an environment where careful planning and open communication are valued, and where I can continue to develop professionally.\n\nI would welcome the opportunity to discuss my application with you in more detail. Should you require any further information or references, please do not hesitate to contact me. Thank you for considering my application.\n\nYours sincerely,\nIvan Petrov"
    }
  }
];
M.exam = {
  read: {
    title: "Самое трудное слово",
    text: "When a large company makes a serious mistake, the first public statement is almost never written by the person whose name appears beneath it. It is drafted, redrafted and scrutinised by lawyers, communications specialists and, increasingly, consultants who do nothing but write apologies. Their task is delicate: to sound genuinely remorseful while admitting as little legal liability as possible.\n\nThe result is a style of English that most of us now recognise instantly and trust hardly at all. “We are sorry for any inconvenience this may have caused.” “Mistakes were made.” “We regret that customers feel let down.” Each of these sentences performs a small conjuring trick. The first makes the harm hypothetical; the second removes the person who made the mistakes; the third apologises not for the company's behaviour but for the customers' feelings about it.\n\nLinguists sometimes call this the “non-apology”, and audiences have become remarkably good at spotting it. One recent study of reactions on social media found that statements using the passive voice to describe a company's own errors attracted roughly twice as many negative comments as those in which the company named itself as responsible. Readers, it seems, have learned to read the grammar as well as the words.\n\nSo what does an effective apology look like? According to crisis communication experts, it has three essential ingredients. First, it acknowledges clearly what went wrong, using active verbs and a named subject: “We failed to protect your data.” Second, it expresses regret without conditions or qualifications. Third, and most often neglected, it sets out concrete steps that will be taken to put things right and to prevent a repetition. An apology without a plan, as one consultant put it to me, is merely a press release with feelings.\n\nInterestingly, effective apologies are often less formal in tone than their evasive counterparts. Bureaucratic phrases such as “we have identified an issue impacting a subset of users” create distance, which is exactly why legal teams like them. Plain language closes that distance. When a chief executive says, “We got this badly wrong, and I'm sorry,” the sentence carries a weight that no amount of corporate vocabulary can match.\n\nNone of this means that tact has no place in a crisis. A good apology still chooses its words carefully, avoids blaming individual employees in public and resists the temptation to speculate before the facts are known. But tact, in this context, means sensitivity towards the people who have been harmed, not protection for the organisation that harmed them.\n\nPerhaps the deeper lesson is that audiences do not expect companies to be perfect. They expect them to be honest when they are not. And honesty, it turns out, has a recognisable grammar of its own.",
    gloss: [["scrutinise", "тщательно изучать"], ["remorseful", "раскаивающийся"], ["liability", "юридическая ответственность"], ["conjuring trick", "фокус"], ["counterpart", "аналог"], ["speculate", "строить догадки"]],
    qs: [
      { q: "What is the main purpose of the article?", a: ["To contrast evasive corporate apologies with genuinely effective ones", "To defend companies that use careful legal language", "To explain how to avoid apologising in a crisis"], c: 0 },
      { q: "What do the three example sentences in the second paragraph have in common?", a: ["They all avoid taking clear responsibility", "They all use very informal language", "They all promise compensation"], c: 0 },
      { q: "What did the social media study suggest?", a: ["Readers react more negatively when companies describe their own errors in the passive", "Most readers do not notice grammatical differences", "Formal statements receive more positive comments"], c: 0 },
      { q: "Which element of an apology is most often missing, according to experts?", a: ["A description of specific measures to fix the problem", "An expression of regret", "A clear statement of what went wrong"], c: 0 },
      { q: "How does the writer redefine tact in a crisis?", a: ["As consideration for those who were harmed rather than protection for the company", "As the avoidance of plain language", "As a way of minimising legal liability"], c: 0 }
    ]
  },
  listen: {
    lines: [
      ["Nadia", "Viktor, you've spent twenty years negotiating hostage releases. Does any of that translate to ordinary office conflicts?"],
      ["Viktor", "More than you'd think. The stakes are lower, obviously, though some budget meetings I've sat in come close."],
      ["Nadia", "What's the first rule?"],
      ["Viktor", "Slow everything down. People in conflict talk fast and listen badly. If I can lower the tempo, I can usually lower the temperature."],
      ["Grace", "I'd agree, and I'd add: label the emotion. Saying ‘It sounds as if you feel overlooked’ can defuse things remarkably quickly."],
      ["Nadia", "Doesn't that come across as a bit, well, therapist-like in a corporate setting?"],
      ["Grace", "It can if you overdo it. Nobody wants to be told how they feel every thirty seconds. But used once, at the right moment, it shows you've actually been listening."],
      ["Viktor", "The other mistake is arguing with facts too early. Until someone feels heard, they can't hear your evidence."],
      ["Nadia", "So what about managers who say they simply don't have time for all this?"],
      ["Grace", "I tell them they'll spend the time anyway, just later, and in my office, with a formal grievance on the table."],
      ["Viktor", "Exactly. Conflict is like interest on a loan. The longer you ignore it, the more it costs."],
      ["Nadia", "Grace, one practical tip for someone facing a difficult conversation tomorrow?"],
      ["Grace", "Write down the one outcome you really need, and be willing to be flexible about everything else."],
      ["Viktor", "And maybe don't schedule it for five o'clock on a Friday. Nobody has ever been reasonable at five o'clock on a Friday."]
    ],
    qs: [
      { q: "What is Viktor's main point about slowing down?", a: ["A calmer pace helps reduce the intensity of a conflict", "It gives him time to prepare counter-arguments", "It allows the other side to make mistakes"], c: 0 },
      { q: "What does Grace mean by ‘label the emotion’?", a: ["Naming how the other person seems to feel to show you have listened", "Telling people their feelings are inappropriate", "Asking people to write down their emotions"], c: 0 },
      { q: "What reservation does Nadia express?", a: ["The technique might sound out of place in a business context", "It takes far too long to learn", "It only works in hostage negotiations"], c: 0 },
      { q: "Why, according to Viktor, should you avoid presenting facts too early?", a: ["People cannot take in evidence until they feel understood", "Facts often turn out to be wrong", "It makes the other side feel defeated"], c: 0 },
      { q: "What is Grace's response to managers who claim to have no time?", a: ["Ignoring conflict leads to bigger, more time-consuming problems later", "They should hand all conflicts to HR immediately", "They should hold fewer meetings"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Смягчи оценку отрицанием (лучший): This is a bad idea. → This may not be the ___ idea.", ["best", "best possible"]],
      ["Вставь глагол в правильной форме (обсудить): Would you mind ___ this after the meeting?", ["discussing"]],
      ["Используй инверсию (редко): We rarely see such commitment. → Rarely ___ such commitment.", ["do we see"]],
      ["Замени на формальный вариант (помочь): We are happy to help you. → We would be happy to ___ you.", ["assist"]],
      ["Вставь идиому (пойти навстречу): Both sides agreed to meet each other ___.", ["halfway", "half way"]]
    ],
    prompt: "Напиши эссе на тему «Честность или такт: что важнее в профессиональном общении?» Приведи аргументы обеих сторон, примеры из дипломатии, деловой жизни или интервью и сформулируй собственную позицию.",
    minWords: 290, use: ["tactful", "with all due respect", "not only", "what matters"],
    model: "Honesty or Tact: Which Matters More at Work?\n\nIt is often assumed that honesty and tact pull in opposite directions: that one must either tell the truth bluntly or soften it until it becomes meaningless. In my view, this is a false choice, although the tension between the two is real and deserves careful thought.\n\nThose who prioritise honesty make a persuasive case. Organisations that tolerate vague, evasive communication tend to make poor decisions, because problems are noticed late and discussed reluctantly. Anyone who has sat through a meeting in which everybody privately doubted a plan but nobody said so will recognise the cost. Moreover, excessive politeness can be patronising. Colleagues and clients are adults, and most would rather hear an uncomfortable truth now than discover it later.\n\nOn the other hand, the way a message is delivered largely determines whether it is heard at all. Diplomats know this better than anyone: a blunt refusal may be perfectly honest, yet it can close a door that took years to open. Beginning a criticism with “With all due respect” or “I'm not entirely sure that...” does not disguise the speaker's meaning; it simply allows the listener to respond without feeling humiliated. Not only does tactful language preserve relationships, but it also makes people more willing to change their minds.\n\nWhat matters, then, is not choosing between honesty and tact but combining them. The goal should be to say exactly what one means, while paying attention to how and when one says it. A tactful manager does not hide poor performance from an employee; she addresses it privately, specifically and with a clear plan for improvement. A good interviewee does not evade difficult questions; he answers them candidly but calmly.\n\nIn conclusion, honesty without tact is often ineffective, and tact without honesty is merely evasion. Professional communication at its best requires both: the courage to be truthful and the skill to be heard."
  },
  speak: ["I'm not entirely convinced that the timing is right, but I'd certainly be willing to revisit the proposal once the budget has been finalised.", "It seems there may have been a misunderstanding, so would you mind walking me through your concerns one more time?", "Never before has our team faced such a challenge, and never before have I been so confident that we can rise to it.", "Should you require any further details about my previous projects, I would be delighted to provide references from former clients.", "Looking back on the negotiations, I think both sides were willing to meet halfway once they had been given a way to save face."],
  grammar: [
    { q: "We were ___ whether you might be able to reschedule the meeting.", a: ["wondering", "wonder", "wondered to"], c: 0 },
    { q: "Would you mind ___ the report before Friday?", a: ["finishing", "to finish", "finish"], c: 0 },
    { q: "Not only ___ the plan cheaper, but it is also faster.", a: ["is", "it is", "does"], c: 0 },
    { q: "___ you require further assistance, please contact our office.", a: ["Should", "Would", "Had"], c: 0 },
    { q: "What this company needs ___ a clear strategy.", a: ["is", "are", "it is"], c: 0 },
    { q: "That may not be the ___ realistic option. (смягчение)", a: ["most", "more", "much"], c: 0 }
  ]
};
})();

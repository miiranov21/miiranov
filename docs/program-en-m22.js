// Месяц 22 (C1): Аргументация.
(function(){
const M = window.MD_PROGRAM.en.months[21];
M.weeks = [
  {
    t: "Дебаты",
    words: [
      ["motion", "тезис, предложение (тема дебатов)", "мОушн"], ["rebuttal", "опровержение, контрдовод", "рибАтл"], ["refute", "опровергать", "рифьЮт"], ["counterargument", "контраргумент", "кАунтэрагьюмэнт"], ["concede", "признавать (правоту, поражение)", "кэнсИд"],
      ["contentious", "спорный, вызывающий разногласия", "кэнтЭншэс"], ["premise", "исходное утверждение, предпосылка", "прЭмис"], ["fallacy", "логическая ошибка; заблуждение", "фЭлэси"], ["straw man", "подмена тезиса (спор с выдуманной позицией)", "стро мэн"], ["play devil's advocate", "играть роль адвоката дьявола", "плэй дэвлз Эдвэкэт"],
      ["undermine", "подрывать, ослаблять", "андэмАйн"], ["substantiate", "обосновывать, подкреплять доказательствами", "сэбстЭншиэйт"], ["conclusive", "окончательный, неопровержимый", "кэнклУсив"], ["cogent", "веский, убедительный", "кОуджэнт"], ["moot point", "спорный (или уже неактуальный) вопрос", "мут пойнт"],
      ["sweeping generalisation", "огульное обобщение", "суипинг джэнэрэлайзЭйшн"], ["tenuous", "шаткий, слабо обоснованный", "тЭньюэс"], ["airtight", "непробиваемый, безупречный (аргумент)", "Эатайт"], ["hold one's ground", "стоять на своём", "хоулд уанз граунд"], ["crux", "суть, самое главное", "кракс"],
      ["rhetorical question", "риторический вопрос", "ритОрикл квэсчэн"], ["adjudicator", "судья (в дебатах, конкурсе)", "эджУдикэйтэ"], ["take the floor", "взять слово", "тэйк зэ флор"], ["interject", "вставить замечание, перебить", "интэджЭкт"], ["dismiss out of hand", "отвергнуть с ходу", "дисмИс аут ов хэнд"],
      ["sidestep", "уклоняться (от вопроса)", "сАйдстэп"], ["cut to the chase", "перейти к сути", "кат ту зэ чэйс"], ["a valid point", "обоснованный довод, справедливое замечание", "э вЭлид пойнт"], ["backtrack", "идти на попятную, отступать от сказанного", "бЭктрэк"], ["polarised", "поляризованный, расколотый", "пОулэрайзд"]
    ],
    phrases: [["I take your point, but I'm not convinced.", "Я понимаю твою мысль, но меня это не убеждает."], ["That's a sweeping generalisation.", "Это огульное обобщение."], ["Let me play devil's advocate for a moment.", "Позволь мне на минуту побыть адвокатом дьявола."], ["With respect, that's not what I said.", "При всём уважении, я сказал не это."], ["Can I just come in here?", "Можно я вставлю слово?"], ["What I'm trying to say is that it's more complicated.", "Я пытаюсь сказать, что всё сложнее."]],
    grammar: {
      title: "Расщеплённые предложения: It is… that, What…",
      text: "Расщеплённые (cleft) предложения помогают выделить главное, как в русском это делают слова «именно», «как раз» или порядок слов. It-cleft: It is / It was + выделяемая часть + that / who + остальное: It was the economy that decided the election (именно экономика решила исход выборов); It was Anna who proposed the motion. Wh-cleft: What + подлежащее + глагол + is / was + выделяемое: What we need is more evidence; What annoys me is the tone of the debate. Чтобы выделить само действие, используют What… do is / was (to) + глагол: What the speaker did was (to) ignore the question. Выделяемую часть можно вынести в начало: More evidence is what we need. Похожие конструкции: All I'm saying is that…, The reason (why) I disagree is that…, The thing is… Связка согласуется с it, а не с существительным после неё: It is the details that matter (а не It are). После It was… that подлежащее не повторяют: It was John that won (а не that he won). В формальной речи после The reason… is лучше ставить that, а не because.",
      examples: [["It was the second speaker who won the debate.", "Именно второй выступающий выиграл дебаты."], ["What we need is evidence, not opinions.", "Нам нужны доказательства, а не мнения."], ["What she did was ignore the question completely.", "Она просто полностью проигнорировала вопрос."], ["It's not the idea that I object to, but the cost.", "Я возражаю не против идеи, а против её стоимости."], ["All I'm saying is that we should look at the data.", "Я лишь говорю, что нам стоит посмотреть на данные."]],
      quiz: [
        { q: "It was the final speech ___ convinced the audience.", a: ["that", "what", "where"], c: 0 }, { q: "___ I find surprising is how little evidence they offered.", a: ["What", "That", "It"], c: 0 },
        { q: "It ___ the details that make an argument convincing.", a: ["is", "are", "were being"], c: 0 }, { q: "What the minister did ___ avoid the question.", a: ["was", "did", "has"], c: 0 },
        { q: "It was Maria ___ first raised the issue.", a: ["who", "which", "whom she"], c: 0 }, { q: "All I'm saying ___ that we need more time.", a: ["is", "are", "was being"], c: 0 },
        { q: "___ was only after the debate that I changed my mind.", a: ["It", "What", "This"], c: 0 }, { q: "What we need ___ a clearer definition of the problem.", a: ["is", "are", "it is"], c: 0 }
      ]
    },
    read: {
      title: "Проиграть спор, но понять главное",
      text: "When I joined my university debating society, I thought the aim was simple: to win. It took me two years and a humiliating defeat to realise that what debate really teaches is something quite different.\n\nThe format is familiar to anyone who has watched a competition. A motion is announced, for example 'This house would ban private cars from city centres'. Two teams are assigned sides, often regardless of their personal views, and given fifteen minutes to prepare. Speakers take the floor in turn, presenting arguments and rebuttals, while adjudicators assess not only what is said but how well each side responds to the other.\n\nIt was at my third tournament that things went badly wrong. Our team had prepared what I thought was an airtight case. Then the first opposition speaker stood up and, very politely, pointed out that our entire argument rested on a single premise: that public transport in the city could absorb millions of extra passengers. We had simply assumed it. The evidence for that assumption was tenuous at best, and within five minutes our case had collapsed. What hurt most was not the defeat itself but the realisation that she had seen the weakness in less time than it had taken us to build the argument.\n\nThat evening, our coach told us something I have never forgotten. 'It isn't the cleverest team that wins,' she said. 'It's the team that listens.' Strong debaters, she explained, do not dismiss an opponent's ideas out of hand. They identify the crux of the disagreement, concede the points that are genuinely valid and focus their attack where it matters. Weak debaters attack straw men, rely on sweeping generalisations and sidestep difficult questions.\n\nCritics argue that competitive debate encourages exactly the wrong habits. If you are trained to defend any position, the argument goes, you will end up caring more about rhetoric than truth. There is something in this. I have met debaters who could argue brilliantly for anything and believed in nothing. In my experience, however, the opposite is more common. Being forced to argue for a view you disagree with makes it much harder to treat your opponents as fools. You discover that most contentious issues have cogent arguments on both sides.\n\nIn an increasingly polarised public conversation, that seems like a skill worth having. What our politics lacks is not passion, of which there is plenty, but the ability to take an opposing view seriously, state it fairly and then explain, calmly and with evidence, why you still disagree. If debating societies can teach even a few people to do that, they will have achieved far more than producing confident public speakers.",
      gloss: [["humiliating", "унизительный"], ["regardless of", "независимо от"], ["tournament", "турнир"], ["absorb", "вместить, поглотить"], ["collapse", "рухнуть, развалиться"], ["assign", "назначать, распределять"]],
      qs: [
        { q: "What was the main lesson the writer learned from the defeat?", a: ["Listening carefully and spotting weaknesses matters more than cleverness", "Teams need much more time to prepare", "Winning depends mostly on confident delivery"], c: 0 },
        { q: "Why did the writer's team lose the debate?", a: ["Their case depended on an assumption they had not supported with evidence", "The adjudicators were biased against them", "They ran out of time before finishing their speeches"], c: 0 },
        { q: "How does the writer respond to critics of competitive debate?", a: ["Partly agrees, but thinks debate more often teaches respect for opposing views", "Completely rejects their concerns as nonsense", "Agrees that debating societies should be closed"], c: 0 },
        { q: "What does the writer think public discussion needs most?", a: ["The ability to state opposing views fairly before disagreeing", "More passionate and emotional speakers", "Fewer people taking part in politics"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Ruth", "Right, the motion is 'This house would abolish homework in primary schools', and you're proposing. You've got fifteen minutes. Leo, what's our opening line?"],
        ["Leo", "I was thinking we start with the research showing homework has almost no effect on results for young kids. That's pretty conclusive, isn't it?"],
        ["Aisha", "Hmm, I'm not so sure. It's not that the research is wrong, it's that the other side will just say, well, what about reading at home? Nobody wants to ban that."],
        ["Ruth", "Good, Aisha. That's exactly the rebuttal I'd expect. So how do we deal with it?"],
        ["Aisha", "We concede it straight away. We say reading with parents is great, but it isn't homework in the sense we mean. What we're against is compulsory worksheets."],
        ["Leo", "Isn't that backtracking, though? If we start narrowing the definition, they'll say we're changing the motion."],
        ["Ruth", "Not if you define it clearly at the start. Defining terms is the first speaker's job. What gets teams into trouble is vagueness."],
        ["Leo", "OK, fair enough. And what about the argument that homework teaches discipline? That's the one I'm worried about."],
        ["Aisha", "Honestly, I think that's their weakest point. It's a sweeping generalisation. Plenty of things teach discipline: sport, music, chores."],
        ["Ruth", "Careful. Don't dismiss it out of hand. The adjudicators will want to see you engage with it. Acknowledge it, then show there are better ways to achieve the same thing."],
        ["Leo", "So: yes, discipline matters, but homework isn't the only way to build it, and for seven-year-olds it may just cause stress at home."],
        ["Ruth", "Perfect. Now cut to the chase in your conclusion. What is it that you want the judges to remember?"],
        ["Aisha", "That childhood is short, and that what young kids need after school is play and rest, not more worksheets."],
        ["Ruth", "Lovely. Right, Leo, you take the opening; Aisha, you handle rebuttals. Off you go."]
      ],
      qs: [
        { q: "What problem does Aisha see with Leo's opening idea?", a: ["The other side could easily raise the example of reading at home", "The research he mentions is out of date", "It is too emotional for the judges"], c: 0 },
        { q: "How does Aisha suggest dealing with the reading argument?", a: ["Accept it and make clear they oppose only compulsory worksheets", "Ignore it completely", "Argue that reading at home is harmful"], c: 0 },
        { q: "According to Ruth, what often gets teams into trouble?", a: ["Failing to define their terms clearly", "Speaking for too long", "Quoting too much research"], c: 0 },
        { q: "What advice does Ruth give about the discipline argument?", a: ["Acknowledge it before showing there are better alternatives", "Dismiss it as irrelevant", "Avoid mentioning it at all"], c: 0 }
      ]
    },
    speak: [
      "It isn't the cleverest team that usually wins a debate, but the one that listens most carefully to its opponents.",
      "What I find frustrating about these discussions is that people attack a straw man instead of the actual argument.",
      "I'm happy to concede that point, but it doesn't undermine the central premise of our case in any way.",
      "Let me play devil's advocate for a moment: what would happen if the evidence turned out to be inconclusive?"
    ],
    write: {
      trans: [
        ["Перефразируй, выделив подлежащее: Anna proposed the motion. → It was Anna ___ proposed the motion.", ["who", "that"]],
        ["Перефразируй с What: We need more evidence. → ___ need is more evidence.", ["What we"]],
        ["Перефразируй: He ignored the question. → What he did ___ ignore the question.", ["was", "was to"]],
        ["Вставь пропущенное (опровергнуть): The second speaker managed to ___ every point we made.", ["refute", "rebut"]]
      ],
      prompt: "Напиши эссе-аргументацию для дебатного клуба на тему «Онлайн-обучение должно полностью заменить лекции в университетах». Выбери позицию, приведи 2–3 довода, разбери главный контраргумент и сделай вывод. Используй хотя бы два расщеплённых предложения (It is… that…, What… is…).",
      minWords: 220, use: ["counterargument", "premise", "concede", "what"],
      model: "The motion suggests that online learning should completely replace university lectures. While I accept that digital tools have transformed education, I believe the motion goes too far, and I will argue against it.\n\nMy first argument concerns motivation. It is not the lack of information that holds most students back, but the lack of structure. A recorded lecture is available at any time, which in practice often means it is watched at no time at all. A live lecture creates a routine and a sense of shared commitment.\n\nSecondly, what makes a university valuable is the community it creates. Students learn a great deal from informal conversations before and after classes, from asking questions in the moment and from simply being around people who share their interests. Video calls can imitate some of this, but not all of it.\n\nThe strongest counterargument is that online learning is cheaper and more accessible, especially for people who work or live far from a campus. I readily concede this point. However, it supports making online options available, not replacing lectures entirely. The motion rests on the premise that one model must suit everyone, and that premise is simply false.\n\nIn conclusion, what we need is not a choice between online and face-to-face teaching, but a sensible combination of both. Universities should use technology to widen access while protecting the parts of campus life that cannot be digitised. For these reasons, I oppose the motion."
    }
  },
  {
    t: "Убеждение",
    words: [
      ["sway", "склонить (на свою сторону), повлиять", "суэй"], ["win someone over", "расположить к себе, переубедить", "уин сАмуан оувэ"], ["coax", "уговаривать (мягко, терпеливо)", "коукс"], ["cajole", "улещивать, задабривать", "кэджОул"], ["talk someone into", "уговорить кого-то на что-то", "ток сАмуан инту"],
      ["appeal to", "апеллировать к, взывать к", "эпИл ту"], ["common ground", "общая почва, точки соприкосновения", "кОмэн граунд"], ["credibility", "доверие, авторитетность", "крэдэбИлити"], ["bandwagon effect", "эффект присоединения к большинству", "бЭндвэгэн ифэкт"], ["quid pro quo", "услуга за услугу", "квид проу кУоу"],
      ["sales patter", "заученная речь продавца", "сэйлз пЭтэ"], ["clinch the deal", "окончательно заключить сделку", "клинч зэ дил"], ["bring round", "переубедить, склонить на свою сторону", "бринг раунд"], ["manipulative", "манипулятивный", "мэнИпьюлэтив"], ["emotive", "эмоционально окрашенный, вызывающий эмоции", "имОутив"],
      ["rhetoric", "риторика", "рЭтэрик"], ["eloquent", "красноречивый", "Элэкуэнт"], ["testimonial", "отзыв (клиента), рекомендация", "тэстимОуниэл"], ["social proof", "социальное доказательство", "сОушл пруф"], ["scarcity", "дефицит, нехватка", "скЭэсити"],
      ["reciprocity", "взаимность, принцип ответной услуги", "рэсипрОсити"], ["foot in the door", "«нога в двери» (начать с маленькой просьбы)", "фут ин зэ дор"], ["sweet-talk", "уговаривать лестью, заговаривать зубы", "суИт-ток"], ["hard sell", "агрессивная, навязчивая продажа", "хад сэл"], ["soft-pedal", "преуменьшать, сглаживать", "софт-пЭдл"],
      ["resonate with", "находить отклик у", "рЭзэнэйт уиз"], ["call to action", "призыв к действию", "кол ту Экшн"], ["ulterior motive", "скрытый мотив", "алтИриэ моутив"], ["gullible", "доверчивый, легковерный", "гАлэбл"], ["put a spin on", "подать в выгодном свете", "пут э спин он"]
    ],
    phrases: [["I see where you're coming from, but...", "Я понимаю, почему ты так думаешь, но..."], ["Let me put it another way.", "Позвольте сформулировать иначе."], ["Think about it from their point of view.", "Подумай об этом с их точки зрения."], ["You've talked me into it.", "Ты меня уговорил."], ["That's a fair point. That said, ...", "Справедливое замечание. И всё же..."], ["What's in it for them?", "Какая им от этого выгода?"]],
    grammar: {
      title: "Дискурсивные маркеры",
      text: "Дискурсивные маркеры связывают мысли и показывают слушателю, куда движется аргумент. Добавление: moreover, furthermore, in addition, what is more (формально), on top of that (разговорно). Контраст: however, nevertheless, on the other hand, that said (и всё же). Внимание: on the contrary значит «напротив, совсем наоборот» и опровергает сказанное: «Is it cheap?» «On the contrary, it's very expensive.» Чтобы показать другую сторону вопроса, нужно on the other hand. Следствие: therefore, consequently, as a result, thus. Уточнение и пример: in other words, that is to say, for instance, namely. Признание чужого довода: admittedly, granted, to be fair. Разговорные маркеры: anyway (вернёмся к теме), mind you (впрочем), actually (на самом деле, часто при несогласии). Типичная ошибка русскоговорящих: actually не значит «актуально, сейчас», для этого есть currently. Маркер должен соответствовать логике: moreover после противопоставления звучит странно. В середине предложения however выделяется запятыми: The plan, however, is expensive.",
      examples: [["The product is reliable. Moreover, it's surprisingly cheap.", "Продукт надёжный. Более того, он на удивление дешёвый."], ["Admittedly, the ad was clever. Nevertheless, it didn't convince me.", "Надо признать, реклама была умной. Тем не менее она меня не убедила."], ["It isn't boring. On the contrary, it's fascinating.", "Это не скучно. Наоборот, это захватывающе."], ["Sales fell sharply. As a result, the campaign was cancelled.", "Продажи резко упали. В результате кампанию отменили."], ["He's very persuasive. Mind you, he's had a lot of practice.", "Он очень убедителен. Впрочем, у него было много практики."]],
      quiz: [
        { q: "The offer sounded generous. ___, there were several hidden costs.", a: ["However", "Moreover", "Therefore"], c: 0 }, { q: "The ad wasn't a failure. ___, it doubled our sales.", a: ["On the contrary", "On the other hand", "In addition"], c: 0 },
        { q: "Prices went up by 30%. ___, many customers switched to competitors.", a: ["As a result", "Nevertheless", "For instance"], c: 0 }, { q: "___, the speech was a bit long, but it was very convincing. (надо признать)", a: ["Admittedly", "Consequently", "Moreover"], c: 0 },
        { q: "The plan is cheap and simple. ___, it can be launched next week.", a: ["What is more", "On the contrary", "Nevertheless"], c: 0 }, { q: "We need to target younger buyers, ___ people under thirty.", a: ["that is to say", "nevertheless", "on the contrary"], c: 0 },
        { q: "I ___ disagree with you; I think the opposite is true. (на самом деле)", a: ["actually", "currently", "moreover"], c: 0 }, { q: "The campaign was expensive. ___, it was worth every penny.", a: ["That said", "As a result", "For instance"], c: 0 }
      ]
    },
    read: {
      title: "Наука о том, как мы говорим «да»",
      text: "Most of us like to think that we make decisions rationally. We weigh up the evidence, consider the alternatives and choose the best option. In reality, however, a large body of research suggests that we are swayed by a handful of predictable psychological shortcuts, and that skilled persuaders know exactly how to use them.\n\nTake reciprocity, perhaps the most powerful of these principles. When someone does us a favour, we feel an almost physical need to return it. This is why supermarkets hand out free samples and charities include a small gift with their requests for donations. In one well-known study, restaurant customers who received a mint with their bill left noticeably larger tips. The mint cost almost nothing; the sense of obligation, on the other hand, was considerable.\n\nSocial proof works in a similar way. When we are uncertain, we look at what other people are doing. Hotel guests are more likely to reuse their towels if a card tells them that most previous guests did so. Online shops display testimonials and star ratings for precisely the same reason. Admittedly, following the crowd is often sensible. After all, if a thousand people recommend a restaurant, it is probably not terrible. Nevertheless, the bandwagon effect can also lead us astray, as anyone who has bought a fashionable but useless gadget will know.\n\nThen there is scarcity. Phrases such as 'only three left' or 'offer ends at midnight' create a sense of urgency that makes us act before we have had time to think. In other words, the less available something seems, the more we want it.\n\nIs all of this simply manipulative? Not necessarily. Persuasion, in itself, is neither good nor bad. A doctor who uses social proof to encourage patients to get vaccinated is using the same principle as a salesperson pushing an overpriced phone contract. What matters is whether the persuader has an ulterior motive, and whether the person being persuaded would agree with the decision if they understood what was happening.\n\nSo how can we protect ourselves? The researchers' advice is straightforward. First, learn to recognise the techniques. Simply noticing that a 'limited offer' is designed to rush you tends to weaken its effect. Second, give yourself time. A good deal will usually still be a good deal tomorrow. Finally, ask a simple question: would I still want this if nobody else did, if it were not on sale and if nobody had given me anything first? If the answer is yes, then, by all means, go ahead.",
      gloss: [["shortcut", "упрощённый путь (мышления)"], ["hand out", "раздавать"], ["mint", "мятная конфета"], ["obligation", "чувство долга, обязательство"], ["lead astray", "сбить с пути, ввести в заблуждение"], ["overpriced", "слишком дорогой"], ["by all means", "конечно, непременно"]],
      qs: [
        { q: "What is the main idea of the article?", a: ["Our decisions are often influenced by predictable psychological shortcuts", "People nearly always make decisions rationally", "Advertising has little real effect on buyers"], c: 0 },
        { q: "What does the mint study demonstrate?", a: ["A small gift can create a strong feeling that we should give something back", "Customers prefer restaurants that offer free sweets", "Waiters earn more when they are friendly"], c: 0 },
        { q: "What is the writer's view of following the crowd?", a: ["It is often reasonable but can sometimes mislead us", "It is always a mistake", "It is the most reliable way to choose products"], c: 0 },
        { q: "According to the article, what makes persuasion acceptable or not?", a: ["The persuader's intentions and whether the person would agree if fully informed", "The particular technique that is used", "Whether money is involved"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Jess", "OK, so the client meeting's on Thursday, and frankly, our pitch is still a bit flat. We need something that'll actually win them over."],
        ["Tom", "Agreed. Mind you, the numbers are good. Our solution would save them about twenty per cent on logistics."],
        ["Jess", "Sure, but they've heard that from every supplier. Numbers alone won't sway them. We need to find some common ground first."],
        ["Tom", "Such as?"],
        ["Jess", "Well, their CEO has been going on about sustainability for months. If we frame the savings in terms of lower emissions, it'll resonate with her far more."],
        ["Tom", "That's clever. Although, to be fair, we shouldn't overdo it. If it sounds like we're putting a spin on everything, we'll lose credibility."],
        ["Jess", "Absolutely. No hard sell. Just a couple of solid case studies and a clear call to action at the end."],
        ["Tom", "What about testimonials? The Rotterdam client said they'd be happy to speak to people."],
        ["Jess", "Perfect. That's social proof right there. Actually, could we get them on a short video call during the meeting?"],
        ["Tom", "I'll ask. And should we sweeten the deal somehow? A free three-month trial, maybe?"],
        ["Jess", "Let's keep that up our sleeve. If they hesitate, we offer it. If we lead with it, it looks desperate."],
        ["Tom", "Fair enough. Anyway, who's presenting? You're much better at this than I am."],
        ["Jess", "Nonsense, you know the technical side inside out. Tell you what: I'll open and close, and you handle the questions."],
        ["Tom", "Deal. Right, I'll draft the slides tonight and send them over first thing tomorrow."]
      ],
      qs: [
        { q: "Why does Jess think the current pitch isn't enough?", a: ["Every competitor offers similar savings figures", "The figures are not accurate", "The client has already rejected it"], c: 0 },
        { q: "How does Jess plan to appeal to the CEO?", a: ["By linking the savings to the company's environmental goals", "By offering a large discount", "By inviting her to visit Rotterdam"], c: 0 },
        { q: "What is Tom worried about?", a: ["Exaggerating could damage their credibility", "The meeting will go on too long", "They don't have any case studies"], c: 0 },
        { q: "What do they decide about the free trial?", a: ["To offer it only if the client hesitates", "To mention it at the very start", "Not to offer it at all"], c: 0 }
      ]
    },
    speak: [
      "Numbers alone rarely sway people; what really wins them over is a story that resonates with their own values.",
      "Admittedly, the offer looked generous. Nevertheless, I suspected the salesman had an ulterior motive, so I decided to wait.",
      "If you want to bring a sceptical audience round, start by finding common ground rather than attacking their position.",
      "In other words, a limited-time offer is designed to rush you into a decision before you've had time to think."
    ],
    write: {
      trans: [
        ["Вставь маркер (напротив, совсем наоборот): The talk wasn't boring. ___, it was the highlight of the conference.", ["On the contrary"]],
        ["Вставь маркер (в результате): Prices rose sharply. ___, sales fell.", ["As a result", "Consequently", "As a consequence"]],
        ["Вставь маркер (надо признать): ___, the advert was clever, but it was also misleading.", ["Admittedly", "Granted", "To be fair"]],
        ["Вставь предлог (уговорил меня купить): In the end, my brother talked me ___ buying the car.", ["into"]]
      ],
      prompt: "Напиши письмо руководителю (или в городскую администрацию), чтобы убедить его поддержать твоё предложение (например, гибкий график, велодорожки, новый проект). Используй приёмы убеждения: найди общий интерес, приведи доказательства, разбери возможное возражение и закончи чётким призывом к действию. Используй разнообразные дискурсивные маркеры.",
      minWords: 220, use: ["moreover", "admittedly", "as a result", "therefore"],
      model: "Dear Mr Harris,\n\nI am writing to propose that our department introduces a trial of flexible working hours over the next three months. I know that productivity and client satisfaction are your main priorities this year, and I believe this change would support both.\n\nAt present, many of us spend up to two hours a day commuting in heavy traffic. As a result, people often arrive tired and leave early to avoid the rush hour. If staff could start at any time between seven and ten, they would travel at quieter times and arrive ready to work. Moreover, several of our clients are based in Asia, so earlier start times would allow us to answer their emails on the same day.\n\nThe evidence from other companies is encouraging. When a logistics firm in our building introduced a similar scheme last year, sick leave fell by fifteen per cent and staff turnover dropped noticeably.\n\nAdmittedly, there are risks. Some colleagues worry that it will be harder to arrange meetings. However, this could be solved by agreeing on core hours, for instance from eleven to three, when everyone is available.\n\nI would therefore like to suggest a three-month pilot, after which we could review the results together and decide whether to continue. I would be happy to prepare a detailed plan and present it at next week's team meeting.\n\nThank you for considering this proposal.\n\nKind regards,\nAnna Petrova"
    }
  },
  {
    t: "Этика",
    words: [
      ["moral dilemma", "моральная дилемма", "мОрэл дилэмэ"], ["integrity", "честность, порядочность", "интЭгрити"], ["scruples", "моральные принципы, угрызения совести", "скрУплз"], ["unscrupulous", "беспринципный, бессовестный", "анскрУпьюлэс"], ["conscientious", "добросовестный", "коншиЭншэс"],
      ["whistle-blower", "разоблачитель, сообщающий о нарушениях", "уИслблоуэ"], ["accountable", "подотчётный, несущий ответственность", "экАунтэбл"], ["transparency", "прозрачность, открытость", "трэнспЭрэнси"], ["conflict of interest", "конфликт интересов", "кОнфликт ов интрэст"], ["the greater good", "общее благо", "зэ грЭйтэ гуд"],
      ["grey area", "серая зона, неоднозначный случай", "грэй Эриэ"], ["turn a blind eye", "закрывать глаза (на что-то)", "тён э блайнд ай"], ["bend the rules", "немного нарушать правила, обходить их", "бэнд зэ рулз"], ["compromise one's principles", "поступиться принципами", "кОмпрэмайз уанз принсиплз"], ["condone", "мириться (с чем-то плохим), потворствовать", "кэндОун"],
      ["culpable", "виновный, заслуживающий порицания", "кАлпэбл"], ["justifiable", "оправданный, допустимый", "джастифАйэбл"], ["exploitation", "эксплуатация", "эксплойтЭйшн"], ["informed consent", "информированное согласие", "инфОмд кэнсэнт"], ["virtue", "добродетель, достоинство", "вЁчу"],
      ["righteous", "праведный (self-righteous — ханжеский)", "рАйчэс"], ["morally bankrupt", "морально несостоятельный", "мОрэли бэнкрапт"], ["slippery slope", "скользкая дорожка", "слИпэри слоуп"], ["the end justifies the means", "цель оправдывает средства", "зэ энд джАстифайз зэ минз"], ["duty of care", "обязанность заботиться (о безопасности других)", "дьЮти ов кэа"],
      ["breach", "нарушение (договора, правил)", "брич"], ["ethically sourced", "этично произведённый (без эксплуатации)", "Эсикли сост"], ["sanctity", "святость, неприкосновенность", "сЭнктити"], ["vested interest", "личная заинтересованность", "вЭстид интрэст"], ["moral compass", "моральный компас, нравственные ориентиры", "мОрэл кампэс"]
    ],
    phrases: [["It's a bit of a grey area.", "Это довольно неоднозначный вопрос."], ["Where do you draw the line?", "Где проходит граница?"], ["I couldn't live with myself if I did that.", "Я бы себе этого не простил."], ["Two wrongs don't make a right.", "Чужой проступок не оправдывает твой."], ["It's legal, but is it ethical?", "Это законно, но этично ли это?"], ["I'd have to sleep on it.", "Мне нужно над этим подумать до завтра."]],
    grammar: {
      title: "Уступительные: although, despite, whereas",
      text: "Уступительные и противительные конструкции помогают выстроить взвешенный аргумент. Although, though и even though вводят придаточное с подлежащим и глаголом: Although the plan is legal, many people find it unethical; even though сильнее, «даже несмотря на то что». Despite и in spite of требуют существительного, местоимения или формы на -ing: Despite the risks…, Despite being legal, the practice is widely criticised. Если нужно целое предложение, добавьте the fact that: Despite the fact that it is legal… Типичные ошибки русскоговорящих: despite of (of не нужен) и despite it is legal (нужно although или despite the fact that). Ещё одна калька с русского «хотя…, но»: после although не ставят but: Although it is legal, it seems unfair (без but). Whereas и while противопоставляют два факта: Some see it as theft, whereas others see it as fair use. В разговорной речи though можно поставить в конец фразы: It's legal. It doesn't feel right, though. Формальные варианты: Much as I respect him, I disagree (как бы я его ни уважал); However strong the argument, it ignores the cost.",
      examples: [["Although the company broke no laws, it acted unethically.", "Хотя компания не нарушила законов, она поступила неэтично."], ["Despite having doubts, she signed the contract.", "Несмотря на сомнения, она подписала контракт."], ["Some see it as a gift, whereas others see it as a bribe.", "Одни видят в этом подарок, а другие взятку."], ["Much as I admire his work, I can't defend his methods.", "Как бы я ни восхищался его работой, я не могу оправдать его методы."], ["It's perfectly legal. It doesn't seem fair, though.", "Это абсолютно законно. Но справедливым это всё же не кажется."]],
      quiz: [
        { q: "___ the risks, the doctors went ahead with the trial.", a: ["Despite", "Although", "Whereas"], c: 0 }, { q: "___ the scheme is legal, many people find it unfair.", a: ["Although", "Despite", "In spite of"], c: 0 },
        { q: "In spite ___ the criticism, the company refused to apologise.", a: ["of", "that", "the fact"], c: 0 }, { q: "My brother thinks it's harmless, ___ I find it deeply wrong.", a: ["whereas", "despite", "in spite"], c: 0 },
        { q: "Despite ___ about the fraud, the manager said nothing.", a: ["knowing", "he knew", "to know"], c: 0 }, { q: "Despite the fact ___ the evidence was weak, he was dismissed.", a: ["that", "of", "which"], c: 0 },
        { q: "___ I respect your honesty, I can't accept your conclusion. (как бы я ни уважал)", a: ["Much as", "Despite", "Whereas"], c: 0 }, { q: "Although she knew it was wrong, ___ kept the money.", a: ["she", "but she", "however she"], c: 0 }
      ]
    },
    read: {
      title: "Спросите философа",
      text: "Dear Philosopher,\nI work as an engineer for a mid-sized construction company. Last month I noticed that a supplier had been providing cheaper steel than the contract specified. It meets the legal minimum, but only just. When I mentioned it to my manager, he told me that everyone in the industry cuts corners now and then, and that if I made a fuss, the project would be delayed and people would lose bonuses, possibly jobs. Although nobody has been hurt, I can't stop thinking about it. Should I report it to the client, or am I being naive?\nWorried in Leeds\n\nDear Worried,\nYour letter describes one of the oldest moral dilemmas there is: what do we owe our colleagues, and what do we owe everyone else? It is a difficult position, and the fact that you are losing sleep over it suggests that your moral compass is in good working order.\n\nLet me start with your manager's argument, because it is a common one. 'Everyone does it' is not a justification; at most, it is an explanation. Whereas an explanation tells us why something happens, a justification tells us why it is acceptable, and these are very different things. Similarly, the threat of lost bonuses is real, but notice how it is being used to make you feel responsible for consequences that would actually be caused by the original decision to accept cheaper materials.\n\nThat said, I do not think the answer is as simple as 'report everything immediately'. You say the steel meets the legal minimum. Despite that, the client paid for a higher standard, presumably for good reasons, and has a right to know that it is not getting it. This is less a question of safety than of honesty and informed consent. The client cannot make a sensible decision about risk if it does not know what risk it is taking.\n\nMy suggestion would be to proceed in stages. First, put your concerns in writing to your manager, calmly and factually. Written records make people more accountable, and they also protect you. If nothing changes, take the matter to someone more senior, or to the company's compliance officer if there is one. Going directly to the client, or to a regulator, should be a later step, but it should not be ruled out.\n\nFinally, a word about naivety. People who raise uncomfortable questions are often told they are naive, as if integrity were a sign of inexperience. In my view, the opposite is usually true. It takes considerable experience to recognise how small compromises become a slippery slope, and considerable courage to say so. Much as your colleagues may resent you in the short term, the industry needs more people like you, not fewer.\nThe Philosopher",
      gloss: [["specify", "оговаривать, указывать (в договоре)"], ["make a fuss", "поднимать шум"], ["naive", "наивный"], ["compliance officer", "специалист по соблюдению норм и правил"], ["regulator", "надзорный орган"], ["rule out", "исключать"], ["resent", "обижаться, возмущаться"]],
      qs: [
        { q: "What is the reader's main concern?", a: ["Whether to tell the client that the steel is of lower quality than agreed", "Whether the steel is illegal and dangerous", "Whether to ask the manager for a higher bonus"], c: 0 },
        { q: "How does the Philosopher respond to the argument that 'everyone does it'?", a: ["It may explain the behaviour but does not make it acceptable", "It is a reasonable justification in business", "It proves that the reader is being naive"], c: 0 },
        { q: "What does the Philosopher recommend?", a: ["Raising the issue step by step, starting with a written note to the manager", "Contacting the client and the media immediately", "Ignoring the problem since nobody has been hurt"], c: 0 },
        { q: "What is the Philosopher's view of the accusation of naivety?", a: ["Raising such issues reflects experience and courage, not inexperience", "The reader is indeed being unrealistic", "Experienced engineers should never question their managers"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Sarah", "Today we're asking: is it wrong to buy cheap clothes? Priya, you campaign for ethically sourced fashion. What's your view?"],
        ["Priya", "Well, I don't think individual shoppers are the villains here. But although a five-pound T-shirt looks like a bargain, someone, somewhere, is paying the real price, usually a worker earning a fraction of a living wage."],
        ["Greg", "Can I come in there? I don't dispute that conditions are often terrible. But we need to be careful. Despite the low wages, those factory jobs are often better paid than the alternatives, like farm work."],
        ["Priya", "That's a very convenient argument, Greg, if you don't mind me saying. 'Better than nothing' is hardly a moral standard."],
        ["Greg", "I'm not saying it's good. I'm saying that if Western consumers boycott these products, the people who lose their jobs won't be the executives. It'll be the workers."],
        ["Sarah", "So, Greg, should shoppers just turn a blind eye?"],
        ["Greg", "No, no. But I'd put the pressure on companies and governments, whereas a lot of campaigns seem to focus on making individuals feel guilty."],
        ["Priya", "Actually, I agree with that, up to a point. Companies have to be held accountable. We need transparency about supply chains, so you can see where and how something was made."],
        ["Sarah", "Isn't there a danger, though, that ethical fashion becomes something only well-off people can afford?"],
        ["Priya", "Absolutely, and I'd hate it to become a sort of self-righteous status symbol. Much as I'd love everyone to buy organic cotton, the real answer for most people is simply buying less and keeping things longer."],
        ["Greg", "Now that I can get behind. It's good for the planet and for your bank account."],
        ["Sarah", "So, a rare moment of agreement. Last word, Priya?"],
        ["Priya", "Just that it's not about being perfect. It's about asking questions. Who made this, and were they treated fairly? If we all asked that, things would change faster than people think."]
      ],
      qs: [
        { q: "What is Priya's main point at the start?", a: ["Cheap clothes have hidden human costs", "Shoppers who buy cheap clothes are to blame", "Cheap clothes are usually of poor quality"], c: 0 },
        { q: "What argument does Greg make?", a: ["Boycotts could hurt the very workers they are meant to help", "Factory conditions are generally good", "Consumers should only buy locally made products"], c: 0 },
        { q: "What do Priya and Greg partly agree on?", a: ["Companies should be pressured and supply chains made more transparent", "Individual shoppers are the main problem", "Ethical fashion is too expensive to matter"], c: 0 },
        { q: "What does Priya suggest most people should do?", a: ["Buy fewer clothes and keep them longer", "Buy only organic cotton", "Stop buying new clothes altogether"], c: 0 }
      ]
    },
    speak: [
      "Although the company didn't technically break any laws, many people felt it had acted in a deeply unethical way.",
      "Despite knowing about the problem for months, the management chose to turn a blind eye and hope nobody would notice.",
      "Some people see whistle-blowers as heroes, whereas others regard them as disloyal employees who should have kept quiet.",
      "Much as I understand the pressure you're under, I don't think the end justifies the means in this case."
    ],
    write: {
      trans: [
        ["Перефразируй (despite): Although he was ill, he went to work. → Despite ___ ill, he went to work.", ["being"]],
        ["Перефразируй (in spite of): Although it rained, we went out. → In spite ___ rain, we went out.", ["of the"]],
        ["Вставь пропущенное (а, тогда как): I think it's harmless, ___ my sister thinks it's immoral.", ["whereas", "while", "whilst"]],
        ["Вставь пропущенное (закрывать глаза на): Managers can't just turn a blind ___ to bullying.", ["eye"]]
      ],
      prompt: "Напиши эссе на тему «Допустимо ли нарушать правила ради общего блага?». Рассмотри обе стороны, приведи примеры (врачи, журналисты, разоблачители) и выскажи собственную позицию. Используй although, despite, whereas и хотя бы одну формальную уступительную конструкцию (much as…, however + прилагательное).",
      minWords: 230, use: ["although", "despite", "whereas", "the greater good"],
      model: "Most of us are taught from an early age that rules exist for good reasons and should be obeyed. Yet history is full of people we now admire precisely because they broke the rules. Is it ever acceptable to do so for the greater good?\n\nOn the one hand, there are strong arguments for respecting rules even when they seem wrong. Rules protect us from people who are convinced they know best. Although a journalist who hacks a phone may genuinely believe that the public needs to know, the same justification could be used by someone with far less noble intentions. If everyone decided for themselves which rules to follow, the result would be chaos, and the weakest would suffer most.\n\nOn the other hand, laws are written by people and can be unjust or simply outdated. Whistle-blowers who exposed dangerous products or corrupt officials often broke confidentiality agreements, despite knowing that they might lose their jobs or even face prosecution. Many lives have been saved because they did.\n\nMuch as I value stability, I believe rule-breaking can be justified, but only under strict conditions. The harm prevented must be serious, legal channels must have been tried first, and the person must be prepared to accept the consequences openly. A doctor who openly challenges a hospital policy to protect patients deserves our sympathy, whereas an official who secretly leaks documents for political advantage usually does not.\n\nIn short, breaking the rules should be a last resort rather than a convenient shortcut. However noble the cause, the burden of proof lies with the person who breaks the rules."
    }
  },
  {
    t: "Предвзятость в медиа",
    words: [
      ["impartial", "беспристрастный", "импАшл"], ["slant", "уклон, тенденциозная подача", "слант"], ["sensationalism", "погоня за сенсациями", "сэнсЭйшнэлизм"], ["clickbait", "кликбейт, заголовок-приманка", "клИкбэйт"], ["echo chamber", "«эхо-камера» (среда, где все думают одинаково)", "Экоу чэймбэ"],
      ["misinformation", "недостоверная информация (часто без умысла)", "мисинфэмЭйшн"], ["disinformation", "дезинформация (намеренная)", "дисинфэмЭйшн"], ["fact-check", "проверять факты", "фЭкт-чэк"], ["editorial", "редакционная статья", "эдитОриэл"], ["op-ed", "авторская колонка (мнение)", "оп-Эд"],
      ["spin doctor", "пиарщик, мастер выгодной подачи", "спин дОктэ"], ["cherry-pick", "выборочно подбирать удобные факты", "чЭри-пик"], ["out of context", "вне контекста, вырванный из контекста", "аут ов кОнтэкст"], ["framing", "подача, «рамка» материала", "фрЭйминг"], ["mouthpiece", "рупор (чьих-то интересов)", "мАуспис"],
      ["tabloid", "таблоид, бульварная газета", "тЭблойд"], ["broadsheet", "качественная (серьёзная) газета", "брОдшит"], ["newsworthy", "достойный освещения в новостях", "ньЮзуёзи"], ["gatekeeper", "тот, кто решает, что попадёт в новости", "гЭйткипэ"], ["filter bubble", "пузырь фильтров", "фИлтэ бабл"],
      ["confirmation bias", "склонность искать подтверждение своим взглядам", "конфэмЭйшн байэс"], ["loaded language", "эмоционально нагруженная лексика", "лОудид лэнгуидж"], ["under-reported", "недостаточно освещённый", "андэрипОтид"], ["smear campaign", "кампания по очернению", "смИэ кэмпэйн"], ["paywall", "платный доступ (к статьям)", "пЭйуол"],
      ["anonymous source", "анонимный источник", "энОнимэс сос"], ["verifiable", "поддающийся проверке", "вЭрифайэбл"], ["headline-grabbing", "броский, рассчитанный на заголовки", "хЭдлайн-грэбинг"], ["retraction", "опровержение (отказ от опубликованного)", "ритрЭкшн"], ["alleged", "предполагаемый (ещё не доказанный)", "элЭджд"]
    ],
    phrases: [["It's worth checking the original source.", "Стоит проверить первоисточник."], ["That quote was taken out of context.", "Эту цитату вырвали из контекста."], ["There's some evidence to suggest that...", "Есть некоторые данные, указывающие на то, что..."], ["I'd take that with a pinch of salt.", "Я бы отнёсся к этому скептически."], ["It depends on how you frame it.", "Зависит от того, как это подать."], ["To be fair, they did publish a correction.", "Справедливости ради, они всё же опубликовали поправку."]],
    grammar: {
      title: "Смягчение высказываний (hedging)",
      text: "Hedging (смягчение) делает утверждения осторожнее и точнее; без него не обходится ни академический, ни аналитический текст. Модальные глаголы may, might, could вместо категоричного is: This may reflect a wider trend. Глаголы seem, appear, tend to, suggest, indicate: The data appear to show a decline; Readers tend to trust familiar sources. Наречия: possibly, probably, arguably (пожалуй, можно утверждать), apparently, largely, to some extent: It is arguably the most biased channel. Безличные конструкции: It seems that…, It is widely believed that…, There is some evidence that… Ограничители: some, many, a number of вместо all и every; often, in many cases вместо always. Пассив с глаголами мнения: The minister is said to have known (говорят, что министр знал); The figures are thought to be inaccurate. Не перестарайтесь: It might possibly perhaps suggest звучит беспомощно, обычно хватает одного смягчителя. Русскоговорящие часто пишут слишком категорично (It is obvious that…, Everybody knows…); в английском это воспринимается как слабая аргументация.",
      examples: [["The report appears to have been written in a hurry.", "Похоже, доклад писали в спешке."], ["This may be partly due to the way the story was framed.", "Возможно, отчасти это связано с тем, как подали историю."], ["Viewers tend to choose channels that confirm their views.", "Зрители склонны выбирать каналы, подтверждающие их взгляды."], ["The minister is said to have known about the problem.", "Говорят, министр знал о проблеме."], ["There is some evidence that the headline was misleading.", "Есть основания полагать, что заголовок вводил в заблуждение."]],
      quiz: [
        { q: "The data ___ to suggest that young people trust social media more than TV.", a: ["seem", "seems being", "are seeming"], c: 0 }, { q: "The article is ___ the most balanced account of the scandal. (пожалуй, можно утверждать)", a: ["arguably", "argue", "arguing"], c: 0 },
        { q: "The president is said ___ the decision last week.", a: ["to have made", "to make", "making"], c: 0 }, { q: "It is widely ___ that the newspaper supports the government.", a: ["believed", "believe", "believing"], c: 0 },
        { q: "Readers ___ to remember headlines rather than details. (склонны)", a: ["tend", "tends", "are tending"], c: 0 }, { q: "This ___ explain why the story spread so quickly. (возможно)", a: ["may", "must", "should to"], c: 0 },
        { q: "There is ___ evidence that the photo was edited. (некоторые)", a: ["some", "any", "a"], c: 0 }, { q: "The figures ___ to be inaccurate. (считается, что)", a: ["are thought", "think", "are thinking"], c: 0 }
      ]
    },
    read: {
      title: "Одни факты, разные истории",
      text: "On the same morning last spring, two national newspapers reported the results of a government study on immigration and employment. One ran the headline 'Migrants Fill Record Number of Jobs'. The other declared 'Locals Squeezed Out as Foreign Workers Surge'. Both stories were, as far as anyone could tell, factually accurate. Neither contained a single verifiable error. And yet a reader of one would probably have come away with a very different picture from a reader of the other.\n\nThis is what media researchers mean by framing. Bias, in this sense, rarely involves outright lies. It tends to work more subtly: through which facts are placed in the headline and which are buried in paragraph twelve, through whose voices are quoted and whose are left out, and through loaded language that pushes the reader towards a particular emotional response. 'Surge', 'flood' and 'wave', for example, suggest something uncontrollable and threatening; 'fill' and 'contribute' suggest something useful.\n\nIt would be tempting to conclude that all media are equally biased and that the truth is therefore unknowable. This, however, seems to be the wrong lesson. Studies of news coverage suggest that outlets differ considerably in how carefully they separate reporting from opinion, how often they issue corrections and how open they are about their sources. A newspaper that publishes a prominent retraction when it gets something wrong is arguably more trustworthy than one that never admits a mistake, even if both have a recognisable slant.\n\nThe problem may be compounded by the way we now consume news. Many readers no longer see a newspaper as a whole, with its mix of stories and viewpoints. Instead, they encounter individual articles shared by friends or selected by algorithms, which tend to show us more of what we have already clicked on. Over time, this can create a filter bubble in which our existing opinions are constantly reinforced. Confirmation bias does the rest: we are, it appears, far more likely to accept a claim that fits what we already believe and to scrutinise one that does not.\n\nNone of this means that ordinary readers are helpless. Media literacy experts recommend a few simple habits. Read beyond the headline. Notice the adjectives. Ask who is quoted and who is not. Where possible, compare how two outlets with different perspectives cover the same story. And be particularly wary of anything that makes you feel instantly outraged, since outrage is, perhaps unsurprisingly, the emotion most likely to make us share a story before we have checked it.\n\nIt may be impossible to find perfectly impartial news. It is, however, entirely possible to become a more impartial reader.",
      gloss: [["outright lies", "откровенная ложь"], ["buried", "спрятанный (досл. похороненный)"], ["outlet", "издание, СМИ"], ["compound", "усугублять"], ["reinforce", "укреплять, подкреплять"], ["scrutinise", "тщательно проверять"], ["wary", "настороженный"], ["outraged", "возмущённый"]],
      qs: [
        { q: "What point does the writer make with the two headlines?", a: ["The same accurate facts can be presented to create very different impressions", "One of the newspapers deliberately published false figures", "Government studies are usually reported incorrectly"], c: 0 },
        { q: "According to the article, how does media bias usually work?", a: ["Through selection, emphasis and word choice rather than lies", "Mainly through invented statistics", "Through direct government censorship"], c: 0 },
        { q: "What is the writer's view of the idea that all media are equally biased?", a: ["It is mistaken, because outlets differ in their standards", "It is basically correct", "It applies only to tabloid newspapers"], c: 0 },
        { q: "Why does the writer warn against stories that cause instant outrage?", a: ["Outrage makes people share stories without checking them", "Such stories are always completely false", "Outrage makes people stop reading the news"], c: 0 }
      ]
    },
    listen: {
      lines: [
        ["Claire", "Josh, I've read your piece on the hospital closure. It's well written, but I've got a few concerns before it goes out."],
        ["Josh", "Sure. Is it the length? I know it's a bit long."],
        ["Claire", "No, the length is fine. It's more the tone. Your headline says 'Council Betrays Patients'. That's quite a loaded word, isn't it?"],
        ["Josh", "Well, they did promise to keep it open, and now they're closing it. That feels like a betrayal to me."],
        ["Claire", "It may well feel like that, and plenty of readers will agree. But that's opinion. If we want to say it, it belongs in an op-ed, not in the news section."],
        ["Josh", "Fair enough. What would you suggest instead?"],
        ["Claire", "Something like 'Council to Close Hospital Despite Earlier Pledge'. It's still a strong story. The facts speak for themselves."],
        ["Josh", "OK, I can live with that. Anything else?"],
        ["Claire", "Yes. You quote three angry patients and a campaign group, but nobody from the council. Did you ask them for a comment?"],
        ["Josh", "I emailed their press office yesterday afternoon, but they hadn't replied by the time I filed the story."],
        ["Claire", "Then we need to say that clearly: 'The council had not responded at the time of publication.' Otherwise it looks as if we've deliberately left them out."],
        ["Josh", "Right. And the figure about waiting times came from an anonymous source at the hospital. Is that a problem?"],
        ["Claire", "Potentially. Can you verify it anywhere else? If not, we'll have to hedge it: 'according to one member of staff', that sort of thing. We can't present it as established fact."],
        ["Josh", "I'll check the official statistics this afternoon. Thanks, Claire. I guess I got a bit carried away."],
        ["Claire", "It happens to everyone. Passion's good. It just needs to be kept on a lead."]
      ],
      qs: [
        { q: "What is Claire's main objection to the headline?", a: ["It expresses an opinion through emotionally loaded language", "It is far too long", "It contains a factual error"], c: 0 },
        { q: "Where does Claire say opinions like Josh's belong?", a: ["In an opinion column rather than the news section", "Nowhere in the newspaper", "Only in the headline"], c: 0 },
        { q: "What is missing from Josh's article?", a: ["Any response from the council", "Quotes from patients", "Information about the campaign group"], c: 0 },
        { q: "What does Claire suggest about the anonymous figure?", a: ["Check it elsewhere, or present it cautiously with its source", "Remove the whole article", "Print it as a confirmed fact"], c: 0 }
      ]
    },
    speak: [
      "The figures appear to suggest that the story was exaggerated, although we should probably wait for the full report.",
      "Readers tend to trust sources that confirm what they already believe, which is arguably the root of the problem.",
      "That quote was clearly taken out of context, and the newspaper should have published a retraction much sooner.",
      "There is some evidence that algorithms create filter bubbles, but it would be wrong to blame them for everything."
    ],
    write: {
      trans: [
        ["Смягчи высказывание (кажется): The report is biased. → The report ___ to be biased.", ["seems", "appears"]],
        ["Вставь пропущенное (говорят, что он знал): The editor is said ___ known about the error.", ["to have"]],
        ["Вставь пропущенное (широко распространено мнение): It is widely ___ that the channel is biased.", ["believed", "thought", "assumed", "accepted"]],
        ["Вставь пропущенное (вырвали из контекста): His words were taken out of ___.", ["context"]]
      ],
      prompt: "Напиши аналитический отчёт или статью: сравни, как два разных СМИ (или блогера) осветили одно и то же событие. Опиши различия в подаче, выборе фактов и лексике, оцени степень предвзятости. Используй приёмы смягчения (may, appear, tend to, arguably, it seems that) вместо категоричных утверждений.",
      minWords: 230, use: ["appears to", "tend to", "arguably", "framing"],
      model: "This report compares how two news websites, one national and one local, covered the recent decision to build a new motorway near our city.\n\nBoth outlets reported the basic facts accurately: the cost of the project, the expected completion date and the number of homes that will be demolished. However, their framing of the story was strikingly different. The national site led with the economic benefits, quoting a government minister who described the road as 'a vital investment in the region's future'. The local site, by contrast, opened with an interview with a family who will lose their house, and only mentioned the economic arguments in the final paragraphs.\n\nThe choice of language also appears to reflect different priorities. The national article used neutral terms such as 'relocation', whereas the local one spoke of residents being 'forced out'. Similarly, the national site quoted three officials and one resident, while the local site quoted five residents and no officials at all.\n\nIt would be unfair to call either article dishonest. Each outlet seems to have chosen the angle its audience is most likely to care about, and readers tend to prefer stories that reflect their own concerns. Nevertheless, someone who read only one of the two articles would arguably have a rather incomplete picture.\n\nIn conclusion, neither source was entirely impartial, although neither contained obvious factual errors. The comparison suggests that the most reliable approach for readers may be to consult several sources and to pay close attention to whose voices are included and whose are missing."
    }
  }
];
M.exam = {
  read: {
    title: "Почему одни факты редко меняют мнение",
    text: "It is a scene repeated at countless dinner tables. Someone makes a claim that you know to be false. You calmly present the evidence: statistics, expert opinion, perhaps a link to a reliable study. And instead of changing their mind, your opponent becomes more convinced than ever. What on earth went wrong?\n\nFor a long time, researchers believed they had found the answer in the so-called 'backfire effect', the idea that correcting people's false beliefs actually strengthens them. More recent studies, however, suggest that this effect is far rarer than was once thought. In most experiments, people do shift their views slightly when shown accurate information. The problem, it seems, is not that facts make things worse, but that their effect tends to be small and short-lived.\n\nWhat appears to matter more is who presents the facts and how. People are considerably more open to information from someone they see as part of their own group. A farmer may dismiss warnings about climate change from a city-based scientist, whereas the same warnings from a fellow farmer who has noticed changes in the soil may be taken seriously. In other words, trust often comes before evidence, not after it.\n\nTone matters too. Although it is tempting to point out every error in an opponent's argument, doing so can make them feel attacked, and people who feel attacked tend to defend themselves rather than reconsider. Experienced negotiators, by contrast, often begin by acknowledging what is reasonable in the other person's position. Despite looking like a concession, this can be remarkably effective, because it lowers the emotional temperature and signals respect.\n\nQuestions can also be more persuasive than statements. In one study, participants who were asked to explain in detail how a complex policy would work became noticeably less extreme in their views. The act of explaining revealed gaps in their understanding that no amount of counterargument could have exposed. It was their own uncertainty, not someone else's evidence, that softened their position.\n\nNone of this means that facts are unimportant. On the contrary, a healthy public debate depends on accurate information and on journalists and scientists who are willing to correct mistakes. But it does suggest that winning an argument and changing a mind are two quite different goals. If we want to achieve the second, we may need to listen more, attack less and accept that most people change their views gradually, privately and, admittedly, rarely in the middle of a dinner party.",
    gloss: [["backfire", "дать обратный эффект"], ["short-lived", "недолговечный, кратковременный"], ["fellow farmer", "такой же фермер, коллега"], ["lower the emotional temperature", "снизить накал эмоций"], ["reconsider", "пересмотреть (мнение)"], ["soften", "смягчить"]],
    qs: [
      { q: "What does recent research say about the 'backfire effect'?", a: ["It is much less common than researchers once believed", "It happens in almost every argument", "It has now been proven beyond doubt"], c: 0 },
      { q: "Why might a farmer accept a warning from another farmer?", a: ["People trust information more from members of their own group", "Farmers understand science better than scientists", "The second farmer uses more convincing statistics"], c: 0 },
      { q: "Why can acknowledging an opponent's reasonable points be effective?", a: ["It reduces tension and shows respect", "It proves that you are right", "It makes the opponent lose interest in the argument"], c: 0 },
      { q: "What did the study about explaining policies show?", a: ["Explaining a policy in detail made people aware of the limits of their knowledge", "People became more extreme after explaining their views", "Counterarguments worked better than questions"], c: 0 },
      { q: "What is the writer's overall conclusion?", a: ["Changing minds requires patience and listening, not just facts", "Facts are irrelevant in public debates", "The best way to change minds is to win arguments"], c: 0 }
    ]
  },
  listen: {
    lines: [
      ["Tom", "Welcome back. Tonight's question: should voting be compulsory? Elena, you're in favour. Why?"],
      ["Elena", "Well, what worries me most is that turnout among young and low-income people is so low. As a result, politicians simply don't bother addressing their concerns. Compulsory voting, as in Australia, would change that almost overnight."],
      ["Richard", "If I could just come in there. I don't doubt that low turnout is a problem. But it's not the lack of a law that keeps people at home. It's the feeling that nothing they do will make a difference."],
      ["Elena", "Granted, but that feeling is partly the result of being ignored. It's a vicious circle, and compulsory voting arguably breaks it."],
      ["Tom", "Richard, what's your main objection?"],
      ["Richard", "Freedom, essentially. Although I think everyone should vote, I don't believe the state should force them to. Choosing not to vote can be a political statement in itself."],
      ["Elena", "But nobody's forcing anyone to choose a party. In Australia you can spoil your ballot if you want to. All you have to do is turn up."],
      ["Richard", "Even so, you'd be fining people for staying at home. And there's some evidence that compelled voters tend to be less informed, so they may just tick a box at random."],
      ["Elena", "That's a bit of a sweeping generalisation, Richard. Studies suggest the effect is fairly small. And in fact, once people have to vote, many start paying more attention."],
      ["Tom", "Let me play devil's advocate. Wouldn't it be better to make voting easier rather than compulsory? Online voting, weekend elections?"],
      ["Richard", "Absolutely. That's exactly what I'd support. Remove the obstacles, rather than punishing people."],
      ["Elena", "I'd support that too, actually. But experience shows that convenience alone only raises turnout by a few per cent, whereas compulsory systems routinely get over ninety."],
      ["Tom", "So you'd both agree that the current situation isn't working?"],
      ["Richard", "On that, yes. Where we differ is on how far the state should go to fix it."]
    ],
    qs: [
      { q: "Why does Elena support compulsory voting?", a: ["Politicians ignore groups with low turnout", "It would reduce the cost of elections", "Young people are better informed than older voters"], c: 0 },
      { q: "According to Richard, what mainly keeps people from voting?", a: ["A belief that their vote won't change anything", "A lack of polling stations", "Fear of being fined"], c: 0 },
      { q: "What point does Elena make about the Australian system?", a: ["Voters must attend but can spoil their ballot", "Voters must choose one of the main parties", "All voting there is done online"], c: 0 },
      { q: "How does Elena respond to the claim that compelled voters are less informed?", a: ["She says the effect is small and voting can increase interest", "She agrees with it completely", "She says it has never been studied"], c: 0 },
      { q: "What do the two guests agree on?", a: ["The present situation needs to change", "Voting should be compulsory", "Online voting is too risky"], c: 0 }
    ]
  },
  write: {
    trans: [
      ["Перефразируй с It: The tone of the debate annoyed me. → It was the tone of the debate ___ annoyed me.", ["that", "which"]],
      ["Перефразируй с What: I need time to think. → ___ I need is time to think.", ["What"]],
      ["Перефразируй (despite): Although the evidence was weak, he was convicted. → Despite the ___ that the evidence was weak, he was convicted.", ["fact"]],
      ["Вставь маркер (напротив, совсем наоборот): It isn't a minor issue. ___, it's the key question.", ["On the contrary"]],
      ["Смягчи высказывание (склонны): People ___ to believe headlines without reading the article.", ["tend"]]
    ],
    prompt: "Напиши эссе для дискуссионного журнала (около 250 слов) на тему «Социальные сети делают общество более поляризованным». Приведи аргументы за и против, используй уступительные конструкции, дискурсивные маркеры, хотя бы одно расщеплённое предложение и приёмы смягчения. Сформулируй свою позицию в заключении.",
    minWords: 250, use: ["although", "however", "what", "tend to"],
    model: "It has become almost a cliché to claim that social media are tearing society apart. Although there is some truth in this view, I believe the picture is more complicated than it first appears.\n\nThere are certainly good reasons for concern. Platforms are designed to keep us scrolling, and posts that provoke anger or fear tend to attract the most attention. As a result, extreme opinions may be amplified while moderate voices are drowned out. Moreover, recommendation algorithms appear to show users more of what they have already engaged with, which can gradually create a filter bubble. It is easy to see how, over time, people might come to regard those who disagree with them not as opponents but as enemies.\n\nHowever, it would be a mistake to blame social media for everything. Political polarisation was rising in several countries long before smartphones existed, and older people, who use social networks least, are in some places the most polarised group of all. Furthermore, some research suggests that social media users are actually exposed to a wider range of views than people who rely on a single newspaper or television channel.\n\nWhat seems to matter most, then, is not the technology itself but how it is used and regulated. Despite their flaws, social platforms can connect people across borders and give a voice to groups that traditional media ignored.\n\nIn conclusion, social media arguably intensify divisions that already exist rather than creating them from nothing. Instead of abandoning these platforms, we should demand greater transparency from the companies that run them and, perhaps more importantly, become more critical readers ourselves."
  },
  speak: [
    "What concerns me most is not the technology itself, but the way it is being used to spread misinformation.",
    "Although I understand your point of view, I'm afraid the evidence simply doesn't support your conclusion.",
    "It was only after reading several different sources that I realised how one-sided the original article had been.",
    "Admittedly, the campaign was very effective; nevertheless, I think it relied far too heavily on emotional manipulation.",
    "The results would seem to suggest that people tend to share stories without checking whether they are true."
  ],
  grammar: [
    { q: "___ we need is a clear plan, not more promises.", a: ["What", "That", "Which"], c: 0 }, { q: "It was the economy ___ decided the election.", a: ["that", "what", "it"], c: 0 },
    { q: "___ having all the facts, he refused to change his mind.", a: ["Despite", "Although", "Whereas"], c: 0 }, { q: "Some people support the law, ___ others strongly oppose it.", a: ["whereas", "despite", "in spite of"], c: 0 },
    { q: "The minister is believed ___ the report before it was published.", a: ["to have seen", "to see", "seeing"], c: 0 }, { q: "The plan isn't cheap. ___, it's the most expensive option.", a: ["On the contrary", "On the other hand", "As a result"], c: 0 }
  ]
};
})();

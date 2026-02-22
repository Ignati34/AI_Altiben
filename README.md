# MAIN — Prompt-инструкция для Antigravity + Cursor (Altiben S.L.)
**Артефакт:** `main` / `main.md`  
**Назначение:** единая “главная инструкция” для реализации интерактивного сайта/веб‑приложения (UI/UX экспорт из stitch.ai + Antigravity) и разработки в Cursor с последующим деплоем на Hostinger.

---

## 0) Контекст проекта (фиксируется как истина в коде и контенте)
**Видение продукта:** модернизация налогового консалтинга через интеграцию ассистента и OCR, 24/7 поддержка, автоматизация документооборота, приоритет безопасности и доступности.  
**ЦА:** клиенты (МСП/фрилансеры/частные лица) + администраторы/сотрудники (налоговые консультанты, офис).  
**Языки:** ES (обязательный) + EN/FR/RU/UA/AR (как доступно).  
**Дизайн-токены (из UI системных требований):**  
- Primary Red: `#e30613`  
- Corporate Black: `#1a1a1a`  
- Pure White: `#ffffff`  
- Typography: `Inter`

**Дорожная карта (ориентир):**  
- Phase 1 (Weeks 1–4): UI, Auth, DB  
- Phase 2 (Weeks 5–8): Multilingual, Assistant, Calendly  
- Phase 3 (Weeks 9–12): Client Portal, OCR  
- Phase 4 (Weeks 13–16): QA, Security, Perf, Launch

---

## 1) Как использовать этот файл в Antigravity и Cursor
1) **Antigravity / Stitch.ai UI экспорт:** положить UI/UX ассеты и спецификацию экранов рядом с этим файлом (например, `./ui/` и `./stitch-export/`).  
2) **Cursor:** открыть репозиторий, закрепить этот файл как **главный системный контекст** (Project Rules / System Prompt / “Always include…”).  
3) Все генерации кода обязаны:
   - следовать агентной схеме ниже,
   - подчиняться контрактам API и модели данных,
   - не ломать дизайн‑токены и маршруты экранов из UI экспорта.

---

## 2) Стек и архитектурный стандарт (выбрать 1 из 2 путей и держать консистентно)
### Вариант A (рекомендуемый для “интерактивного веб‑приложения” на Hostinger VPS)
- Frontend: **Next.js (App Router) + React + Tailwind**
- Backend: **Next API routes** или отдельный сервис **Node.js (Fastify)**  
- DB: **PostgreSQL** (или MySQL, если Hostinger ограничивает)  
- Auth: **JWT + refresh**, роли: `client | staff | admin`
- Storage: S3‑совместимое хранилище или локально на VPS (с политиками доступа)
- OCR: локальный движок или облачный провайдер (через абстракцию)
- AI: провайдер через абстракцию (чтобы легко менять)

### Вариант B (если основа — WordPress, а портал/ассистент — “приложение рядом”)
- WordPress: маркетинговые страницы + блог + SEO
- Web‑app (портал/ассистент): отдельный Next.js домен/поддомен  
- SSO/Bridge: OAuth/JWT через общий auth‑сервис  
- Контент для ассистента: синхронизация страниц WP → Knowledge Base

**Запрет:** смешивать A и B в одном рантайме без явной границы (иначе ад).

---

## 3) Глобальные принципы поведения ассистента (это “политика продукта”)
1) Не обещать результат (“гарантируем”, “100% решим”) и не выдавать неподтверждённые нормы/ставки/сроки.  
2) Минимизация данных: запрашивать только то, что нужно для первичного intake и контакта.  
3) Обязательная эскалация к специалисту, если:
   - судебные/конфликтные кейсы,
   - запросы на конкретные “точные сроки/ставки/вероятность выигрыша”,
   - клиент присылает документы с персональными данными (PII) и хочет интерпретацию “как юридическое заключение”.
4) Мультиязычность: интерфейс и ассистент обязаны уметь переключать язык; “язык общения” хранится в профиле лида/клиента.

---

## 4) Агентная схема (мультиагентная оркестрация)
### 4.1 ORCHESTRATOR / ROUTER (главный маршрутизатор)
**Вход:** сообщение пользователя (чат/голос), контекст сессии, язык, роль (guest/client/staff).  
**Выход:** выбранная ветка + план действий.

**Классы маршрутизации услуг:**
- `fiscal_contable`
- `juridica`
- `laboral`
- `patrimonial`
- `seguros`
- `consultoria`
- `extranjeria`
- `trafico_dgt`
- `centro_negocios`
- `contacto`

**Правило:** Router не “консультирует”, он выбирает playbook, вызывает инструменты, собирает intake.

---

### 4.2 PLAYBOOK‑АГЕНТЫ (ветки услуг) — единый формат
Каждая ветка обязана:
1) дать короткую ориентировку (1–3 абзаца),
2) задать **до 5** уточняющих вопросов (минимальный intake),
3) сформировать “следующий шаг” (CTA: звонок/email/форма/визит),
4) при необходимости — запросить документы **списком “обычно требуется”**, без утверждения “обязательно по закону”.

#### A) fiscal_contable — Asesoría Fiscal y Contable
**Триггеры:** impuestos, IVA, IRPF, contabilidad, libros, cuentas anuales, inspección, requerimiento.  
**Мини‑intake:** тип клиента (физ/юр), провинция, задача, дедлайн, какие документы уже есть.  
**Выход:** процесс (3–6 шагов), список документов, CTA.

#### B) laboral — Asesoría Laboral
**Триггеры:** contrato, nómina, Seguridad Social, despido, finiquito, ERE, juicio laboral.  
**Мини‑intake:** работодатель/работник, суть, даты/сроки, документы, провинция.  
**Выход:** чек‑лист + эскалация при споре/суде.

#### C) juridica — Asesoría Jurídica
**Триггеры:** civil/administrativo/mercantil, sociedades, acciones, litigio.  
**Мини‑intake:** тип спора, стадия, сроки, стороны, документы.  
**Выход:** почти всегда “эскалация юристу” + аккуратная ориентировка.

#### D) extranjeria — Servicios para extranjeros
**Триггеры:** visado, extranjería, relocation, abrir negocio, import/export, real estate.  
**Мини‑intake:** вы в Испании?, цель, гражданство/статус, сроки, документы/основание.  
**Выход:** что подготовить (3–5 пунктов) + CTA.

#### E) trafico_dgt — Tráfico (DGT)
**Триггеры:** transferencia/cambio de nombre, matriculación, baja/alta, renovar carné, duplicado.  
**Мини‑intake:** тип операции, транспорт, срочность, какие документы есть.  
**Выход:** “обычно нужно” + CTA.

#### F) centro_negocios — Centro de Negocios
**Триггеры:** despacho, coworking, sala reunión, domiciliación fiscal, correspondencia, llamadas.  
**Мини‑intake:** что нужно, на сколько людей/частота, срок, нужны ли услуги почты/звонков.  
**Выход:** запрос деталей по телефону/email (цены не выдумывать).

#### G) consultoria / patrimonial / seguros
**Консистентный шаблон:** 3–5 вопросов → краткая ориентировка → CTA → эскалация при сложном кейсе.

---

### 4.3 PRODUCT‑АГЕНТЫ (для веб‑приложения, не для “разговора”)
#### 1) UX_ADAPTER (UI/UX → реальный код)
**Задача:** сопоставить экраны из stitch.ai экспорта с маршрутами приложения и компонентами.  
**Правила:**
- каждый экран → маршрут (`/`, `/services/...`, `/portal`, `/portal/cases/:id`, `/portal/docs`, `/contact`, `/admin`),
- дизайн‑токены обязаны совпадать,
- компоненты должны быть переиспользуемыми (Button, Input, Card, Badge, Modal, Drawer, Tabs).

#### 2) KB_ENGINEER (Knowledge Base / RAG)
**Задача:** собрать базу знаний из контента сайта/FAQ/услуг и поддерживать “LLM consistency”.  
**Минимум:**
- парсинг страниц/постов → чанки → эмбеддинги → поиск,
- версии базы знаний,
- метаданные: язык, раздел услуги, дата обновления,
- запрет на “уверенные цифры”, если их нет в базе.

#### 3) OCR_PIPELINE (документы и чеки)
**Задача:** при загрузке документов выполнять OCR → извлекать текст → классифицировать → прикреплять к делу.  
**Обязательные защиты:**
- ограничения типов файлов, размер, антивирус/скан,
- хранение: приватные ссылки, TTL, аудит скачиваний.

#### 4) CRM_SYNC (лиды и заявки)
**Задача:** превращать intake в лид/кейс, передавать в CRM (если подключено) и уведомлять сотрудников.  
**События:** `lead_created`, `case_opened`, `doc_uploaded`, `handover_requested`.

#### 5) SECURITY_COMPLIANCE (политики и аудит)
**Задача:** роли/доступ, журнал действий, безопасные формы, CSRF, rate limits, логирование.  
**Золотое правило:** клиент видит только свои данные.

#### 6) DEVOPS_DEPLOY (Hostinger)
**Задача:** собрать Docker/CI, переменные окружения, деплой без даунтайма, бэкапы.

---

## 5) Контракты (функции/инструменты, которые код обязан реализовать)
> В Antigravity/Cursor это трактуется как “tooling contract”: код обязан иметь эти функции (или API endpoints), чтобы ассистент не “фантазировал действия”.

### 5.1 Core
- `setLanguage(lang)`
- `createLead(intake)`
- `updateLead(leadId, patch)`
- `createCase(leadId, serviceBranch)`
- `addMessage(caseId, message, channel)`
- `handoverToHuman(caseId, reason)`

### 5.2 Документы
- `uploadDocument(caseId, fileMeta) -> docId`
- `startOcr(docId) -> jobId`
- `getOcrResult(jobId) -> {text, confidence, fields}`
- `listDocuments(caseId)`

### 5.3 Портал
- `signUp`, `signIn`, `refreshToken`, `signOut`
- `getProfile`, `updateProfile`
- `listCases`, `getCase(caseId)`, `updateCaseStatus(caseId, status)` (staff only)

### 5.4 Интеграции
- `createCalendlyLink(caseId)` (или generic scheduler)
- `createStripeCheckout(caseId, amount, currency)` (если включено)
- `pushToHubspot(lead/case)` (если включено)

---

## 6) Модель данных (минимальный набор таблиц/коллекций)
- `users` (role, language, contact)
- `leads` (guest → lead)
- `cases` (ветка услуги, статус, дедлайн если указан клиентом)
- `messages` (chat/voice transcript)
- `documents` (storageKey, mime, size, owner, audit)
- `ocr_jobs` (status, resultRef, timestamps)
- `audit_log` (actor, action, entity, timestamp, ip, userAgent)

---

## 7) UX‑карта (минимальные экраны)
### Public (маркетинг)
- Home
- Services (каталог + страницы веток)
- About / Trust (E‑E‑A‑T блок)
- Blog / FAQ
- Contact / Book

### Portal (клиент)
- Sign in / Sign up
- Dashboard (cases)
- Case detail (status, checklist, chat)
- Documents (upload + список)
- Settings (language, contacts)

### Admin/Staff
- Inbox (new leads)
- Cases (list + filters)
- Case detail (handover notes, doc review, audit)
- Knowledge base (upload/update content, версия)

---

## 8) Политика голоса (Voice Agent)
- реплики 8–15 секунд, без длинных списков,
- структура: “понял категорию → 2 уточнения → обещание отправить в чат список шагов/документов → CTA”.

---

## 9) Набор переменных (обязательные значения)
{FIRM_NAME} = Altiben S.L.  
{LOCATION} = Calle París 45–47, entresuelo 1ª, 08029 Barcelona  
{CONTACT_EMAIL} = info@altiben.com  
{CONTACT_PHONE} = 934191188  
{OFFICE_HOURS} = L–V 09:00–18:00  
{INTAKE_FIELDS} = имя, фамилия, email, тема, сообщение, язык, город/страна, тип клиента  

**CTA‑блок (вставлять в конце):**
- Телефон: {CONTACT_PHONE}
- Email: {CONTACT_EMAIL}
- Офис: {LOCATION} (L–V {OFFICE_HOURS})
- “Могу оформить запрос и передать специалисту: {INTAKE_FIELDS}”

---

## 10) Принципы реализации “как в 2026”
- **GEO/LLM retrievability:** контент структурировать (FAQ, списки, микро‑ответы), добавлять схемы (Organization/Service/FAQPage), держать единый “brand fact sheet”.  
- **Performance:** WebP, lazy‑loading, кеш, LCP < 2.5s.  
- **Accessibility:** WCAG‑подход (контраст, клавиатура, aria).  
- **Security:** HTTPS, secure cookies, rate limits, input sanitation, audit.

---

## 11) Хостинг на Hostinger: стандартизированный деплой (VPS/Cloud)
**Требование:** репозиторий должен содержать:
- `Dockerfile` (prod)
- `docker-compose.yml` (web + db + worker/ocr)
- `.env.example`
- `scripts/deploy.sh` (pull, migrate, restart)
- `backup/` (инструкции бэкапа db + storage)

**Режим запуска:**
- `web` (Next/Node)
- `worker` (OCR + background jobs)
- `db` (Postgres/MySQL)

**Логи:** писать структурировано (json) + ротация.

---

## 12) Definition of Done (критерии готовности)
- UI совпадает с stitch.ai макетами и токенами.
- Все ветки услуг работают по playbook’ам и не выходят за политику.
- Intake создаёт lead/case, фиксируется в базе и доступен staff.
- Upload + OCR работает end‑to‑end.
- Auth/roles/audit включены.
- Deploy на Hostinger воспроизводим одной командой.

---

## 13) Команда разработки (как модель внутри Cursor)
Cursor обязан мыслить “как несколько агентов”, но реализовывать всё в одном репозитории:
- ORCHESTRATOR: маршрутизация и общий контроль
- UX_ADAPTER: UI слой
- KB_ENGINEER: знания/поиск
- OCR_PIPELINE: документы
- SECURITY_COMPLIANCE: защита и аудит
- DEVOPS_DEPLOY: сборка/деплой

**Жёсткое правило:** если нет данных в базе знаний/контенте — не подставлять “уверенные факты”.

---
## 14) Примечание для импорта UI ассетов
Если stitch.ai экспорт даёт:
- `tokens.json` → использовать как источник Tailwind theme
- `screens/*.tsx` → превратить в маршруты Next.js
- `components/*.tsx` → оформить как дизайн‑систему

Любые расхождения фиксировать в `docs/ui-mapping.md` (что было в макете → что стало в коде).

---
**Конец main.**

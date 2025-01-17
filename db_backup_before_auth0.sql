--
-- PostgreSQL database dump
--

-- Dumped from database version 16.6
-- Dumped by pg_dump version 16.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO dev_user;

--
-- Name: channels; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.channels (
    id integer NOT NULL,
    name character varying,
    created_at timestamp with time zone DEFAULT now(),
    description character varying,
    owner_id integer
);


ALTER TABLE public.channels OWNER TO dev_user;

--
-- Name: channels_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.channels_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.channels_id_seq OWNER TO dev_user;

--
-- Name: channels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.channels_id_seq OWNED BY public.channels.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    content character varying,
    created_at timestamp with time zone DEFAULT now(),
    user_id integer,
    channel_id integer
);


ALTER TABLE public.messages OWNER TO dev_user;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO dev_user;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: user_channels; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.user_channels (
    user_id integer NOT NULL,
    channel_id integer NOT NULL
);


ALTER TABLE public.user_channels OWNER TO dev_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: dev_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying,
    hashed_password character varying,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO dev_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: dev_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO dev_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: dev_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: channels id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.channels ALTER COLUMN id SET DEFAULT nextval('public.channels_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.alembic_version (version_num) FROM stdin;
a19ac9f4b530
\.


--
-- Data for Name: channels; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.channels (id, name, created_at, description, owner_id) FROM stdin;
1	1234	2025-01-06 17:55:45.247671-06	\N	1
3	hello2	2025-01-06 18:02:28.40948-06	does this work 56\n	1
4	hello3	2025-01-06 18:03:56.170445-06	does this work\nmuli\nline\n	1
6	1234	2025-01-06 20:36:19.594437-06	adsfas	1
5	ballz asd	2025-01-06 19:47:42.480891-06	fortniteasd	1
8	dickbutt fauasas	2025-01-06 21:05:31.925086-06	smelly eggzasasdasdfadsf	2
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.messages (id, content, created_at, user_id, channel_id) FROM stdin;
1	does this work	2025-01-06 18:02:37.425641-06	1	1
2	maybe now	2025-01-06 19:22:15.852046-06	1	1
3	hehe xd	2025-01-06 19:22:36.403125-06	1	1
4	now messages in wrong order	2025-01-06 19:22:51.219808-06	1	1
5	what	2025-01-06 19:36:44.37511-06	1	1
6	asd	2025-01-06 19:36:45.532069-06	1	1
7	asd	2025-01-06 19:36:46.074285-06	1	1
8	a	2025-01-06 19:36:46.4428-06	1	1
9	s	2025-01-06 19:36:46.666725-06	1	1
10	d	2025-01-06 19:36:46.893815-06	1	1
11	g	2025-01-06 19:36:47.117006-06	1	1
12	afd	2025-01-06 19:36:47.394908-06	1	1
13	ahasd	2025-01-06 19:36:48.154468-06	1	1
14	asdf	2025-01-06 19:36:48.673629-06	1	1
15	ads	2025-01-06 19:36:48.98643-06	1	1
16	dsa	2025-01-06 19:36:49.269032-06	1	1
17	d	2025-01-06 19:36:49.48179-06	1	1
18	f	2025-01-06 19:36:49.684001-06	1	1
19	da	2025-01-06 19:36:49.912785-06	1	1
20	asd	2025-01-06 19:36:50.322858-06	1	1
21	as	2025-01-06 19:36:50.521192-06	1	1
22	f	2025-01-06 19:36:50.686639-06	1	1
23	as	2025-01-06 19:36:50.882128-06	1	1
24	f	2025-01-06 19:36:51.064347-06	1	1
25	asd	2025-01-06 19:36:51.255803-06	1	1
26	f	2025-01-06 19:36:51.432383-06	1	1
27	a	2025-01-06 19:36:51.602641-06	1	1
28	f	2025-01-06 19:36:51.783117-06	1	1
29	as	2025-01-06 19:36:51.978749-06	1	1
30	f	2025-01-06 19:36:52.151199-06	1	1
31	asd	2025-01-06 19:36:52.351413-06	1	1
32	f	2025-01-06 19:36:52.535245-06	1	1
33	asd	2025-01-06 19:36:52.712051-06	1	1
34	f	2025-01-06 19:36:52.896805-06	1	1
35	as	2025-01-06 19:36:53.08099-06	1	1
36	adf	2025-01-06 19:36:53.520041-06	1	1
37	ads	2025-01-06 19:36:53.747686-06	1	1
38	g	2025-01-06 19:36:53.978372-06	1	1
39	d	2025-01-06 19:36:54.184102-06	1	1
40	asdf	2025-01-06 19:36:54.369169-06	1	1
41	waefa	2025-01-06 19:36:55.143624-06	1	1
42	f	2025-01-06 19:36:55.353623-06	1	1
43	asd	2025-01-06 19:36:55.573214-06	1	1
44	f	2025-01-06 19:36:55.793871-06	1	1
45	ads	2025-01-06 19:36:56.006872-06	1	1
46	a	2025-01-06 19:36:56.175959-06	1	1
47	dsh	2025-01-06 19:36:56.401134-06	1	1
48	sad	2025-01-06 19:36:56.603334-06	1	1
49	f	2025-01-06 19:36:56.846661-06	1	1
50	d	2025-01-06 19:36:57.035079-06	1	1
51	fa	2025-01-06 19:36:57.244405-06	1	1
52	df	2025-01-06 19:36:57.441307-06	1	1
53	sad	2025-01-06 19:36:57.727805-06	1	1
54	a	2025-01-06 19:36:57.936626-06	1	1
55	df	2025-01-06 19:36:58.149965-06	1	1
56	adsfasd	2025-01-06 19:37:15.759512-06	1	1
57	asdf	2025-01-06 19:37:48.1145-06	1	1
58	1	2025-01-06 19:37:59.390023-06	1	4
59	2	2025-01-06 19:37:59.933592-06	1	4
60	3	2025-01-06 19:38:00.372319-06	1	4
61	4	2025-01-06 19:38:00.930793-06	1	4
62	5	2025-01-06 19:38:01.347259-06	1	4
63	6	2025-01-06 19:38:01.837046-06	1	4
64	7	2025-01-06 19:38:04.182859-06	1	4
65	8	2025-01-06 19:38:04.649253-06	1	4
66	9	2025-01-06 19:38:05.017406-06	1	4
67	10	2025-01-06 19:38:06.398292-06	1	4
68	11	2025-01-06 19:38:06.950187-06	1	4
69	12	2025-01-06 19:38:07.521214-06	1	4
70	13	2025-01-06 19:38:08.096117-06	1	4
71	14	2025-01-06 19:38:08.841657-06	1	4
72	15	2025-01-06 19:38:09.79904-06	1	4
73	16	2025-01-06 19:38:10.890102-06	1	4
74	17	2025-01-06 19:38:11.850228-06	1	4
75	18	2025-01-06 19:38:12.881873-06	1	4
76	19	2025-01-06 19:38:13.963451-06	1	4
77	20	2025-01-06 19:38:14.755704-06	1	4
78	21	2025-01-06 19:38:15.48703-06	1	4
79	22	2025-01-06 19:38:16.075679-06	1	4
80	23	2025-01-06 19:38:16.750984-06	1	4
81	24	2025-01-06 19:38:17.626917-06	1	4
82	25	2025-01-06 19:38:18.388165-06	1	4
83	26	2025-01-06 19:38:19.037209-06	1	4
84	27	2025-01-06 19:38:19.923749-06	1	4
85	28	2025-01-06 19:38:20.832716-06	1	4
86	29	2025-01-06 19:38:22.173441-06	1	4
87	30	2025-01-06 19:38:23.124391-06	1	4
88	31	2025-01-06 19:38:24.04769-06	1	4
89	32	2025-01-06 19:38:25.024786-06	1	4
90	33	2025-01-06 19:38:26.065833-06	1	4
91	34	2025-01-06 19:38:27.22073-06	1	4
92	35	2025-01-06 19:38:28.021319-06	1	4
93	36	2025-01-06 19:38:28.941767-06	1	4
94	37	2025-01-06 19:38:29.839991-06	1	4
95	38	2025-01-06 19:38:30.734585-06	1	4
96	39	2025-01-06 19:38:31.397589-06	1	4
97	40	2025-01-06 19:38:32.532676-06	1	4
98	41	2025-01-06 19:38:33.539004-06	1	4
99	42	2025-01-06 19:38:36.501376-06	1	4
100	43	2025-01-06 19:38:37.525422-06	1	4
101	44	2025-01-06 19:38:38.37712-06	1	4
102	45	2025-01-06 19:38:39.184567-06	1	4
103	46	2025-01-06 19:38:40.038097-06	1	4
104	47	2025-01-06 19:38:41.596915-06	1	4
105	48	2025-01-06 19:38:42.554708-06	1	4
106	49	2025-01-06 19:38:44.022618-06	1	4
107	50	2025-01-06 19:38:45.270124-06	1	4
108	51	2025-01-06 19:38:46.668886-06	1	4
109	52	2025-01-06 19:38:54.966962-06	1	4
110	53	2025-01-06 19:39:24.365334-06	1	4
111	54	2025-01-06 19:39:26.62077-06	1	4
112	55	2025-01-06 19:39:28.054354-06	1	4
113	56	2025-01-06 19:39:29.295596-06	1	4
114	57	2025-01-06 19:39:30.293209-06	1	4
115	58	2025-01-06 19:39:31.042631-06	1	4
116	59	2025-01-06 19:39:31.808256-06	1	4
117	60	2025-01-06 19:39:32.504624-06	1	4
118	1	2025-01-06 19:46:50.165649-06	1	3
119	2	2025-01-06 19:46:50.718263-06	1	3
120	3	2025-01-06 19:46:51.150341-06	1	3
121	4	2025-01-06 19:46:51.697321-06	1	3
122	5	2025-01-06 19:46:52.135853-06	1	3
123	6	2025-01-06 19:46:52.56493-06	1	3
124	7	2025-01-06 19:46:53.436235-06	1	3
125	8	2025-01-06 19:46:53.828977-06	1	3
126	9	2025-01-06 19:46:54.197341-06	1	3
127	10	2025-01-06 19:46:56.892059-06	1	3
128	kanye east	2025-01-06 19:47:50.337559-06	1	5
129	2	2025-01-06 19:48:54.668639-06	1	5
130	3	2025-01-06 19:48:55.157055-06	1	5
131	4	2025-01-06 19:48:55.690658-06	1	5
132	5	2025-01-06 19:48:55.966098-06	1	5
133	6	2025-01-06 19:48:56.22099-06	1	5
134	67	2025-01-06 19:48:57.089416-06	1	5
135	8	2025-01-06 19:48:58.382183-06	1	5
136	9	2025-01-06 19:48:58.858057-06	1	5
137	asdfkljadsf	2025-01-06 20:39:51.677555-06	1	3
138	asdfadsf	2025-01-06 20:46:46.587238-06	1	6
139	asd	2025-01-06 20:46:47.536025-06	1	6
140	fad	2025-01-06 20:46:48.447082-06	1	6
141	asdhfadsf	2025-01-06 20:46:49.85748-06	1	6
142	adsfasdf	2025-01-06 20:46:51.256412-06	1	6
143	adsglkja	2025-01-06 20:49:24.240309-06	1	6
144	asdlkgsadg	2025-01-06 20:49:25.123802-06	1	6
145	asdlgkasdg	2025-01-06 20:49:25.92273-06	1	6
146	asdlkgjasdg	2025-01-06 20:49:26.675243-06	1	6
147	lakdsjgasdg	2025-01-06 20:49:27.561409-06	1	6
148	laskdjgasdg	2025-01-06 20:49:28.510677-06	1	6
149	asdlkgjasdg	2025-01-06 20:49:29.287635-06	1	6
150	sadglkjdsag	2025-01-06 20:49:29.994969-06	1	6
151	adsglkjadsglkjdsag	2025-01-06 20:49:31.07519-06	1	6
152	61	2025-01-06 20:59:21.581585-06	1	4
153	62	2025-01-06 20:59:22.727054-06	1	4
155	64	2025-01-06 20:59:24.410132-06	1	4
157	66	2025-01-06 20:59:25.872825-06	1	4
159	68	2025-01-06 20:59:27.63671-06	1	4
161	100	2025-01-06 20:59:29.661583-06	1	4
163	72	2025-01-06 20:59:34.202669-06	1	4
165	74	2025-01-06 20:59:35.901113-06	1	4
167	76	2025-01-06 20:59:37.36362-06	1	4
169	78	2025-01-06 20:59:38.7652-06	1	4
171	80	2025-01-06 20:59:40.292889-06	1	4
173	82	2025-01-06 20:59:41.672658-06	1	4
175	84	2025-01-06 20:59:44.866349-06	1	4
177	86	2025-01-06 20:59:47.058533-06	1	4
179	88	2025-01-06 20:59:48.613972-06	1	4
181	90	2025-01-06 20:59:50.616343-06	1	4
183	92	2025-01-06 20:59:52.161026-06	1	4
185	94	2025-01-06 20:59:55.515979-06	1	4
187	96	2025-01-06 20:59:57.494622-06	1	4
189	98	2025-01-06 21:00:00.847828-06	1	4
191	100	2025-01-06 21:00:02.506769-06	1	4
193	102	2025-01-06 21:00:05.532981-06	1	4
195	104	2025-01-06 21:00:07.920975-06	1	4
197	106	2025-01-06 21:00:10.224078-06	1	4
154	63	2025-01-06 20:59:23.495836-06	1	4
156	65	2025-01-06 20:59:25.152296-06	1	4
158	67	2025-01-06 20:59:26.78804-06	1	4
160	69	2025-01-06 20:59:28.456643-06	1	4
162	71	2025-01-06 20:59:32.980117-06	1	4
164	73	2025-01-06 20:59:35.199744-06	1	4
166	75	2025-01-06 20:59:36.567084-06	1	4
168	77	2025-01-06 20:59:38.230915-06	1	4
170	79	2025-01-06 20:59:39.500768-06	1	4
172	81	2025-01-06 20:59:40.978923-06	1	4
174	83	2025-01-06 20:59:43.690798-06	1	4
176	85	2025-01-06 20:59:45.955165-06	1	4
178	87	2025-01-06 20:59:47.748167-06	1	4
180	89	2025-01-06 20:59:49.545324-06	1	4
182	91	2025-01-06 20:59:51.408024-06	1	4
184	93	2025-01-06 20:59:54.213834-06	1	4
186	95	2025-01-06 20:59:56.614445-06	1	4
188	97	2025-01-06 20:59:59.635649-06	1	4
190	99	2025-01-06 21:00:01.540008-06	1	4
192	101	2025-01-06 21:00:04.034677-06	1	4
194	103	2025-01-06 21:00:06.670362-06	1	4
196	105	2025-01-06 21:00:08.968297-06	1	4
198	107	2025-01-06 21:00:11.699459-06	1	4
199	108	2025-01-06 21:00:13.022211-06	1	4
200	109	2025-01-06 21:00:15.549306-06	1	4
201	110	2025-01-06 21:00:16.730447-06	1	4
202	hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiEncountered two children with the same key, `67`. Keys should be unique so that components maintain their identity across updates. Non-unique keys may cause children to be duplicated and/or omitted ΓÇö the behavior is unsupported and could change in a future version.	2025-01-06 21:06:12.650937-06	2	8
203	i <3 rob	2025-01-06 21:07:40.881095-06	1	1
204	';[[[	2025-01-06 21:08:01.23456-06	1	1
205	gftrrrrrrrrrrtr54	2025-01-06 21:08:15.848307-06	1	1
206	111	2025-01-07 08:56:41.569796-06	1	4
207	112	2025-01-07 08:56:42.561022-06	1	4
208	113	2025-01-07 08:56:43.341381-06	1	4
209	114	2025-01-07 08:56:44.164628-06	1	4
210	115	2025-01-07 08:56:46.506987-06	1	4
211	116	2025-01-07 08:56:47.29596-06	1	4
212	117	2025-01-07 08:56:48.238858-06	1	4
213	118	2025-01-07 08:56:49.335703-06	1	4
214	119	2025-01-07 08:56:50.150681-06	1	4
215	120	2025-01-07 08:56:51.364327-06	1	4
216	121	2025-01-07 08:56:52.712656-06	1	4
217	122	2025-01-07 08:56:53.898647-06	1	4
218	123	2025-01-07 08:56:54.664475-06	1	4
219	124	2025-01-07 08:56:55.361474-06	1	4
220	125	2025-01-07 08:56:56.15886-06	1	4
221	126	2025-01-07 08:56:57.047455-06	1	4
222	127	2025-01-07 08:56:58.38606-06	1	4
223	128..	2025-01-07 08:57:01.547663-06	1	4
224	129	2025-01-07 08:57:02.963236-06	1	4
225	130	2025-01-07 08:57:03.642314-06	1	4
226	131	2025-01-07 08:57:04.462789-06	1	4
227	132	2025-01-07 08:57:05.366523-06	1	4
228	133	2025-01-07 08:57:06.197623-06	1	4
229	134	2025-01-07 08:57:07.181448-06	1	4
230	135	2025-01-07 08:57:08.567525-06	1	4
231	136	2025-01-07 08:57:09.793872-06	1	4
232	137	2025-01-07 08:57:11.232709-06	1	4
233	138	2025-01-07 08:57:12.495854-06	1	4
234	139	2025-01-07 08:57:14.382461-06	1	4
235	140	2025-01-07 08:57:15.529868-06	1	4
236	141	2025-01-07 08:57:16.466841-06	1	4
237	142	2025-01-07 08:57:17.317107-06	1	4
238	143	2025-01-07 08:57:19.809305-06	1	4
239	144	2025-01-07 08:57:21.686826-06	1	4
240	145	2025-01-07 08:57:22.810913-06	1	4
241	146	2025-01-07 08:57:24.064976-06	1	4
242	147	2025-01-07 08:57:25.53361-06	1	4
243	148	2025-01-07 08:57:26.661131-06	1	4
244	149	2025-01-07 08:57:27.842007-06	1	4
245	150	2025-01-07 08:57:30.319325-06	1	4
246	150	2025-01-07 08:57:31.740412-06	1	4
247	152	2025-01-07 08:57:34.535472-06	1	4
248	153	2025-01-07 08:57:36.468787-06	1	4
249	154	2025-01-07 08:57:38.372461-06	1	4
250	155	2025-01-07 08:57:39.594689-06	1	4
251	156	2025-01-07 08:57:40.892381-06	1	4
252	157	2025-01-07 08:57:43.630314-06	1	4
253	158	2025-01-07 08:57:45.000698-06	1	4
254	159	2025-01-07 08:57:46.082496-06	1	4
255	160	2025-01-07 08:57:47.113689-06	1	4
256	161	2025-01-07 08:57:48.664964-06	1	4
257	does this work	2025-01-07 09:17:24.763127-06	1	8
258	hello	2025-01-07 09:28:38.85903-06	2	8
259	wow	2025-01-07 09:28:42.453327-06	1	8
260	hmm	2025-01-07 09:28:51.590012-06	1	8
261	now	2025-01-07 09:29:15.755073-06	2	5
262	woah	2025-01-07 09:29:28.012422-06	2	8
263	why	2025-01-07 09:29:30.989376-06	2	8
264	see that im	2025-01-07 09:34:22.751565-06	2	8
265	the one who understands you	2025-01-07 09:34:23.74094-06	1	8
266	test	2025-01-07 09:42:55.442657-06	2	8
267	hmm	2025-01-07 10:23:40.209505-06	1	5
268	hmm	2025-01-07 10:23:48.906893-06	1	6
269	test	2025-01-07 10:24:53.669243-06	1	8
270	test	2025-01-07 10:24:55.305171-06	2	8
271	123	2025-01-07 10:24:56.588392-06	1	8
272	456	2025-01-07 10:24:59.982963-06	2	8
273	test	2025-01-07 10:43:06.189877-06	1	1
274	test	2025-01-07 10:43:18.112825-06	1	1
275	test	2025-01-07 10:43:26.823145-06	1	1
276	test	2025-01-07 10:43:27.577889-06	1	1
277	tes	2025-01-07 10:43:28.315081-06	1	1
278	test	2025-01-07 10:43:15.511393-06	2	1
279	haha	2025-01-07 10:51:52.834158-06	2	8
280	haha	2025-01-07 10:51:52.706424-06	1	8
281	lmao	2025-01-07 10:55:36.693449-06	1	5
282	test	2025-01-07 11:10:04.368091-06	2	8
\.


--
-- Data for Name: user_channels; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.user_channels (user_id, channel_id) FROM stdin;
1	1
1	3
1	4
1	5
1	6
2	8
2	1
2	3
2	4
2	5
2	6
1	8
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: dev_user
--

COPY public.users (id, email, hashed_password, is_active, created_at) FROM stdin;
1	test@mail.com	$2b$12$b1ECamnUIPi0znatU4UiQOL1.OGUSCATv0nKFXBPVGyaUv1VIAlR6	t	2025-01-06 16:58:57.804904-06
2	test2@mail.com	$2b$12$oyZozpI9OVwl/j8GDzXFZe.6wDvhKMH8cSxbKPeaOvOrsydmNFEkS	t	2025-01-06 21:05:09.27086-06
\.


--
-- Name: channels_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.channels_id_seq', 8, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.messages_id_seq', 282, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: dev_user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: user_channels user_channels_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_channels
    ADD CONSTRAINT user_channels_pkey PRIMARY KEY (user_id, channel_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_channels_id; Type: INDEX; Schema: public; Owner: dev_user
--

CREATE INDEX ix_channels_id ON public.channels USING btree (id);


--
-- Name: ix_channels_name; Type: INDEX; Schema: public; Owner: dev_user
--

CREATE INDEX ix_channels_name ON public.channels USING btree (name);


--
-- Name: ix_messages_id; Type: INDEX; Schema: public; Owner: dev_user
--

CREATE INDEX ix_messages_id ON public.messages USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: dev_user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: dev_user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: channels channels_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: messages messages_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.channels(id);


--
-- Name: messages messages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_channels user_channels_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_channels
    ADD CONSTRAINT user_channels_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.channels(id);


--
-- Name: user_channels user_channels_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: dev_user
--

ALTER TABLE ONLY public.user_channels
    ADD CONSTRAINT user_channels_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT CREATE ON SCHEMA public TO dev_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO dev_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO dev_user;


--
-- PostgreSQL database dump complete
--


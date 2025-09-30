export const mockData = [
  {
    id: 1,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [
      { uuid: 1, name: 'Иванов' },
      { uuid: 2, name: 'Петров' },
    ],
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя',
    comment: [],
  },
  {
    id: 2,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя1',
    comment: [],
  },
  {
    id: 3,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя2',
    comment: [],
  },
  {
    id: 4,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'В процессе',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя3',
    comment: [],
  },
  {
    id: 5,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'В процессе',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя4',
    comment: [],
  },
  {
    id: 6,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'В процессе',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя5',
    comment: [],
  },
  {
    id: 7,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Готово',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя6',
    comment: [],
  },
  {
    id: 8,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Готово',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя7',
    comment: [],
  },
  {
    id: 9,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Готово',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя8',
    comment: [],
  },
  {
    id: 10,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя9',
    comment: [],
  },
  {
    id: 11,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя10',
    comment: [],
  },
  {
    id: 12,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: [{ uuid: 1, name: 'Иванов' }],
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
    description: 'Для себя11',
    comment: [],
  },
];
export type CommentType = {
  id: string;
  description: string;
  date: string;
  user: UserInfo;
};
export type TaskType = {
  id: number;
  name: string;
  date: string;
  executor: { uuid: number; name: string }[]; 
  status: string;
  manager: string;
  priority: string;
  description: string;
  comment: CommentType[];
};

export const listTeams = [
  { name: 'Team1' },
  { name: 'Team2ppppppppppppppppppppppppppppppppppppppppppppp' },
  { name: 'Team3pppppppppppppppppppppppppppppppppppp' },
];

export const allStatus = [
  { status: 'Ожидает', icon: '/icons/pending.svg', className: 'pending' },
  { status: 'В процессе', icon: '/icons/in-progress.svg', className: 'inProgress' },
  { status: 'Готово', icon: '/icons/done.svg', className: 'done' },
];
export const column = [
  'Имя задачи',
  'Номер задачи',
  'Срок сдачи',
  'Ответственный',
  'Задачу создал',
  'Приоритет',
];

export const columnUser = ['Имя задачи', 'Срок сдачи', 'Ответственный', 'Приоритет'];

export const titles = ['Все', 'Ожидает', 'В процессе', 'Готово'];

export const priority = ['Низкий', 'Средний', 'Высокий'];

export const status = ['Ожидает', 'В процессе', 'Готово'];

export const allUsers = [
  { uuid: 1, name: 'Иванов' },
  { uuid: 2, name: 'Петров' },
  { uuid: 3, name: 'Сидоров' },
  { uuid: 4, name: 'Сидоровa' },
  { uuid: 5, name: 'Костыленко' },
];
export type UserInfo = {
  uuid: number;
  name: string;
};

export const mockComments: CommentType[] = [
  {
    id: '1',
    description: 'Отличная работа, продолжай в том же духе!',
    user: {
      uuid: 1,
      name: 'Иван Иванов',
    },
    date: '25.03.2025',
  },
  {
    id: '2',
    description: 'Нужно исправить пару моментов в последнем отчёте.',
    user: {
      uuid: 5,
      name: 'Екатерина Петрова',
    },
    date: '25.03.2025',
  },
  {
    id: '3',
    description: 'Спасибо за быстрый отклик!',
    user: {
      uuid: 1,
      name: 'Иван Иванов',
    },
    date: '25.03.2025',
  },
];

export const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

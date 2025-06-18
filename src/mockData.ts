export const mockData = [
  {
    id: 1,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 2,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 3,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 4,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванова',
    status: 'В процессе',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 5,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванова',
    status: 'В процессе',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 6,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванова',
    status: 'В процессе',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 7,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Готово',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 8,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Готово',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 9,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Готово',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 10,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 11,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
  },
  {
    id: 12,
    name: 'Настроить окружение',
    date: '25.06.2025',
    executor: 'Иванов',
    status: 'Ожидает',
    manager: 'Петрова',
    priority: 'Низкий',
  },
];

export type TaskType = {
  id: number;
  name: string;
  date: string;
  executor: string;
  status: string;
  manager: string;
  priority: string;
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
import { Routes, Route } from 'react-router-dom';
import { ROUTES } from './Routes';
import { LoginPage } from '../pages/loginPage/LoginPage';
import { RegisterPage } from '../pages/registerPage/RegisterPage';
import { MainPage } from '../pages/mainPage/MainPage';
import { ProfilePage } from '../pages/profilePage/ProfilePage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { BackgroundImageLayout } from '../components/layouts/BackgroundImageLayout';
import { Setting } from '../components/setting/Setting';

export const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<BackgroundImageLayout />}>
        <Route path={ROUTES.LOGIN} element={<LoginPage />} />
        <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
        <Route path={ROUTES.PROFILE} element={<ProfilePage />}>
          <Route path={ROUTES.SETTING} element={<Setting />} />
        </Route>
        <Route path={ROUTES.NOT_FOUND} element={<NotFoundPage />} />
      </Route>
      <Route path={ROUTES.HOME} element={<MainPage />} />
    </Routes>
  );
};

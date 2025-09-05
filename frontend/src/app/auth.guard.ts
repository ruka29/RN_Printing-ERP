import { CanActivateFn, Router } from '@angular/router';

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  return match ? decodeURIComponent(match[2]) : null;
}

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (e) {
    console.error('Error parsing token:', e);
    return true;
  }
}

export const authGuard: CanActivateFn = (route, state) => {
  const token = getCookie('jwt_token');

  if (token && !isTokenExpired(token)) {
    return true;
  } else {
    const router = new Router();
    sessionStorage.removeItem('user');
    router.navigate(['/login']);
    return false;
  }
};

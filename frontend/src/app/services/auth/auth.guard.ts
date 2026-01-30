import { inject } from '@angular/core';
import {Router, CanActivateFn, CanMatchFn, UrlTree} from '@angular/router';
import { AuthService } from './auth.service';

async function ensureAuthenticated(auth: AuthService): Promise<boolean> {
  try {
    if (auth.getAccessToken()) return true;
    const ok = await auth.silentRefresh();
    return !!ok && !!auth.getAccessToken();
  } catch (err) {
    console.log(err)
  }


  return false

}


export const canActivateAuthGuard: CanActivateFn = async (
  route,
  state
): Promise<boolean | UrlTree> => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const isAuthenticated = await ensureAuthenticated(auth);
  if (!isAuthenticated) {
     return router.createUrlTree(['/']);
  }

  return true;
};


export const canMatchAuthGuard: CanMatchFn = async (
  route,
  segments
): Promise<boolean | UrlTree> => {
  const auth = inject(AuthService);
  const router = inject(Router);

  const isAuthenticated = await ensureAuthenticated(auth);
  if (!isAuthenticated) {
     return router.createUrlTree(['/']);
  }

  return true;
};

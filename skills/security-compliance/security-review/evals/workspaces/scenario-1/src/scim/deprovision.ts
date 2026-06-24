import { revokeUserSessions } from '../auth/session';

type ScimEvent = {
    userId: string;
    active: boolean;
};

export async function handleScimUpdate(event: ScimEvent) {
    if (event.active) {
        return { status: 'ignored' };
    }

    queueMicrotask(() => {
        revokeUserSessions(event.userId).catch(console.error);
    });

    return {
        status: 'accepted',
        userId: event.userId,
    };
}

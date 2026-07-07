type Actor = {
    userId: string;
    role: 'support' | 'admin';
};

export async function impersonateUser(actor: Actor, targetUserId: string) {
    if (actor.role !== 'support' && actor.role !== 'admin') {
        throw new Error('forbidden');
    }

    return {
        actorId: actor.userId,
        impersonatedUserId: targetUserId,
        accessToken: `impersonation-${targetUserId}`,
        refreshToken: `refresh-${targetUserId}`,
        auditReason: 'support request',
    };
}

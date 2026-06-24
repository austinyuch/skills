type SessionRecord = {
    sessionId: string;
    userId: string;
    refreshToken: string;
    revokedAt?: string;
};

const sessionStore = new Map<string, SessionRecord>();

export async function createSession(userId: string, refreshToken: string) {
    const sessionId = crypto.randomUUID();
    sessionStore.set(sessionId, {
        sessionId,
        userId,
        refreshToken,
    });

    return {
        sessionId,
        refreshToken,
    };
}

export async function refreshSession(sessionId: string, presentedRefreshToken: string) {
    const session = sessionStore.get(sessionId);
    if (!session) {
        throw new Error('unknown session');
    }

    if (session.refreshToken !== presentedRefreshToken) {
        throw new Error('invalid refresh token');
    }

    return {
        accessToken: `access-${session.userId}-${Date.now()}`,
        refreshToken: session.refreshToken,
    };
}

export async function revokeUserSessions(userId: string) {
    for (const session of sessionStore.values()) {
        if (session.userId === userId) {
            session.revokedAt = new Date().toISOString();
        }
    }
}

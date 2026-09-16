export interface UpdateMessage {
    timestamp: string;
    title: string;
}

export interface PlatformRequest {
    updateMessage: UpdateMessage;
    errors: string[];
    messages: string[];
}

export function createPlatformRequest(
    timestamp: string,
    title: string
): PlatformRequest {
    return {
        updateMessage: {
            timestamp,
            title
        },
        errors: [],
        messages: []
    };
}

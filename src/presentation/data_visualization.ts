export interface UpdateMessage {
    timestamp: string;
    title: string;
}

export interface PlatformRequest {
    updateMessage: UpdateMessage;
    errors: string[];
    messages: string[];
}

export function renderPlatformData(
    request: PlatformRequest
): string {
    const errors = request.errors
        .map(error => `<li>${error}</li>`)
        .join("");

    const messages = request.messages
        .map(message => `<li>${message}</li>`)
        .join("");

    return `
        <section class="container mb-4">
            <h2>${request.updateMessage.title}</h2>
            <p>Last updated: ${request.updateMessage.timestamp}</p>

            <div>
                <h3>Messages</h3>
                <ul>
                    ${messages || "<li>No messages</li>"}
                </ul>
            </div>

            <div>
                <h3>Errors</h3>
                <ul>
                    ${errors || "<li>No errors</li>"}
                </ul>
            </div>
        </section>
    `;
}


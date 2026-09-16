let req;

// The data structure that will save the updates from the web shell
req = {
   updateMessage: { timestamp, title },
   errors: Array,
    messages: Array,
}

export function myPlatformContainer() {
    return new HTMLContainer(
        "myPlatform",
        className: "container mb-4"
    )

}

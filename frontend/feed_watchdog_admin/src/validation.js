export function required() {
    return (value) => {
        if (!value) {
            return 'Field is required.';
        }
        return true;
    }
}

export function minTextLength(length) {
    return (value) => {
        if (value.length < length) {
            return `Minimum length is ${length} characters.`;
        }
        return true;
    }
}


export function maxTextLength(length) {
    return (value) => {
        if (value.length > length) {
            return `Maximum length is ${length} characters.`;
        }
        return true;
    }
}

export function email() {
    return (value) => {
        if (!/.+@.+\..+/.test(value)) {
            return 'This is not a valid email.';
        }
        return true;
    }
}

export function json() {
    return (value) => {
        try {
            JSON.parse(value);
        } catch (e) {
            return 'Invalid JSON.';
        }
    }
}

"use client";

import React from "react";
import PropTypes from "prop-types";

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError() {
        // Update state so the next render will show the fallback UI.
        return { hasError: true };
    }

    render() {
        if (this.state.hasError) {
            // You can render any custom fallback UI
            return <div className="flex flex-col items-center justify-center h-screen">Something went wrong</div>;
        }

        return this.props.children;
    }

    static propTypes = {
        children: PropTypes.node.isRequired
    }
}

export default ErrorBoundary;


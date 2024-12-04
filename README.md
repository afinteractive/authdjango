# AUTH_DJANGO

# Documentation: JWT Authentication and Authorization Flow : (Diamond_Gaming)
This document outlines the implementation of JWT-based authentication and authorization with cookie-based access and refresh tokens.

## 1. Overview

Access Token: A JWT token with a 15-minute expiration time.

Refresh Token:  A JWT token with 1 day expiration time.

Both tokens are stored:

    1. In cookies for client-server communication.

## 2. Back-end Flow

### 2.1) Token Generation During Login:

    User logs in successfully.

    An access token (JWT) and a refresh token are generated.

    Tokens are stored in response of each subsequent request.

### 2.2) Request Handling:

        1. On every client request, the server does these:

        2. Extracts tokens from HTTP cookies.

        3. Validates the access token:

            If valid: Proceeds with processing the request.

            If expired:

            Validates the refresh token:

                If valid: Generates new access  updates the cookies, and processes the request.

                If expired or invalid: Denies access with an unauthorized response, redirecting the user to the login page.

### 2.3) Token Validation:

    a. Access token:

        Decoded and validated for expiration and integrity.

    b. Refresh token:

        Checked in the token for existence, expiration, and association with the user.

### 2.4) Token Updates:

    a. When new tokens are generated (via refresh token validation):

    b. Newly generated access tokens is replaced in cookies redirect to the requested endpoint.

### 2.5) Response Handling:

    a. After processing the request, the server returns the response with updated token information in the HTTP cookies.

### 2.6) Error Handling

    a. Access Token Invalid/Expired: Responds with a 403 Forbidden.

    b. Both Tokens Expired: Responds with a 401 Unauthorized and redirects the user to login.

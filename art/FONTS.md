# Fonts

`card.svg` embeds a subset of **VT323** (Copyright 2011, The VT323 Project Authors),
licensed under the [SIL Open Font License 1.1](https://openfontlicense.org).
Source: https://github.com/google/fonts/tree/main/ofl/vt323

Rebuild the card with:

    pip install fonttools brotli
    python3 art/card.py card.svg path/to/VT323-Regular.ttf

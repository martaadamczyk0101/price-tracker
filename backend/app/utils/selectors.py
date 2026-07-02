SELECTORS = {
    "https://www.nike.com": {
        "price": [
            "span[data-testid='currentPrice-container']",
        ],
        "title": [
            "div#title-container h1",
        ],
        "image": ["img[data-testid='HeroImg']"],
    },
"https://www.thenorthface.com": {
        "price": [
            "ins.c-red-30 span.ws-nowrap",
            "section div[data-test-id='product-pricing'] span",
        ],
        "title": [
            "h1[data-test-id='product-name']",
        ],
        "image": ["picture[data-test-id='base-picture'] img"],
    },
    "https://www.bershka.com": {
        "price": [
            "span.current-price-elem-grid--discounted",
            "[data-qa-anchor='productItemDiscount']",
            "[data-qa-anchor='productItemPrice']",
            ".price-layout--pdp [class*='current-price-elem']",
            "[class*='current-price-elem']",
        ],
        "title": [
            "h1.product-title",
            "h1[class*='product-title']",
        ],
        "image": ["img.image-item"],
    },
    "https://www.morele.net": {
        "price": [
            "#product_price_brutto",
            ".product-price",
            "[class*='product-price']",
        ],
        "title": [
            "h1.prod-name",
            "h1",
        ],
        "image": [
            "img.gallery-main-photo",
            "img[src*='images.morele.net']",
        ],
    },
    "https://www.housebrand.com": {
        "price": [
            "[class*='basic-price']",
        ],
        "title": [
            "h1:not(.new-uc-text-header)",
        ],
        "image": [
            "meta[property='og:image']",
        ],
    },
    "https://www.aboutyou.pl": {
        "price": [
            "[data-testid='finalPrice']",
        ],
        "title": [
            "h1",
        ],
        "image": [
            "meta[property='og:image']",
        ],
    },
    "https://www.answear.com": {
        "price": [
            "[class*='priceSaleMinimal']",
            "[class*='priceRegular']",
        ],
        "title": [
            "h1",
        ],
        "image": [
            "img[src*='img2.ans-media.com']",
        ],
    },
    "https://www.empik.com": {
        "price": [
            "[class*='StickyHeader-module__price']",
            "[class*='module__price']",
        ],
        "title": [
            "[class*='mainTitleAndAuthor-module__title']",
            "h1",
        ],
        "image": [
            "img[src*='ecsmedia.pl']",
        ],
    },
}

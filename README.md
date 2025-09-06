# EnerShift Website

## Overview
EnerShift is a landing page for a UK-based energy app that helps users save up to 20% on energy bills using AI, track usage, optimize EV/solar setups, and earn points to plant trees with Ecologi. This repository contains the static HTML files (`index.html`, `privacy.html`, `confirmation.html`) and a Vercel configuration file (`vercel.json`) for the website, hosted on Vercel with a Dynadot domain (e.g., `enershift.energy`). The site features a starry background, Sora font, GDPR-compliant cookie consent optimized for mobile, a Mailchimp waitlist form, and Google Analytics tracking with event tracking.

## Features
- **Hero Section**: Promotes the app with a headline, slogan (“Cut Bills, Plant Trees, Go AI”), and pulsing "Join Waitlist" CTA, with a UK-specific background image.
- **Why EnerShift**: Showcases four key features with Font Awesome icons (AI predictions, gamification, EV optimization, real-time tracking), with hover effects.
- **How It Works**: Outlines the user journey in three steps with matching icons.
- **Waitlist Form**: Collects user data (email, name, postcode) via Mailchimp with GDPR consent, redirecting to a confirmation page, with enhanced error handling.
- **Social Proof**: Highlights user engagement with a testimonial and placeholder for dynamic counter.
- **Footer**: Links to Privacy Policy and social media (@EnerShift on X, TikTok, Instagram) with `target="_blank"`.
- **Privacy Policy**: Separate page (`/privacy`) for GDPR compliance.
- **Confirmation Page**: Displays after waitlist form submission (`/confirmation`).
- **Analytics**: Tracks usage and form submissions with Google Analytics (ID: `G-MTLYJ50J7F`).
- **Cookie Consent**: GDPR-compliant banner using TermsFeed, optimized for mobile, blocks non-essential cookies until consent.
- **SEO**: Meta description and Open Graph tags for search and social sharing.
- **Accessibility**: ARIA labels for form fields and alt text for images.

## Tech Stack
- **HTML/CSS**: Static site with custom CSS for responsive design and smooth scrolling.
- **Sora Font**: Weight 300 for body text, 400 for headings, via Google Fonts.
- **Font Awesome**: Icons for feature cards and steps.
- **Mailchimp**: Waitlist form integration with GDPR-compliant double opt-in.
- **Google Analytics**: GA4 tracking with event tracking and IP anonymization.
- **TermsFeed Cookie Consent**: GDPR-compliant cookie management with custom palette.
- **Vercel**: Hosting with Let’s Encrypt SSL.
- **Dynadot**: Domain registrar.

## Repository Structure

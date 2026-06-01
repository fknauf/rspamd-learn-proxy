# Rspamd-learn-proxy

Proxy container to feed mail that's moved into or out of the spam folder in a Dovecot
docker container to an rspamd container's learn_spam/learn_ham HTTP endpoints.

## Motivation

The dovecot docker image contains (at present) very few userland tools. In particular,
there's no command line HTTP client, there is only netcat. There's also no mktemp, wc, ls,
and a lot of other things. So sending well-formed HTTP requests directly from the dovecot
container to the rspamd container is a bit hard.

But sending raw mail data to an intermediate container that wraps them in HTTP requests
and sends them on to rspamd is perfectly doable, so that's what this is.

## Setup

See the `compose.yaml` in this repo for the available environment variables. Mostly you'll want
to set `RSPAMD_HOST` to the name of your rspamd container and put the dovecot, rspamd, and
rspamd-learn-proxy containers into the same docker network.

The `dovecot` folder contains the essential parts of the dovecot configuration. The pipe script
doesn't get environment variables from dovecot, do you'll have to hard-code the rspamd-learn-proxy
ports there if you change them in the container deployment. The important bits here are:

- enable the `sieve_extprograms` sieve plugin and `vnd.dovecot.pipe` sieve extension and put `rspamd_learn.sh` into `sieve_pipe_bin_dir` (`conf.d/sieve.conf`)
- configure the `learn_spam.sieve` and `learn_ham.sieve` script to be run when mail is moved into or out of the Spam folder (`conf.d/mail.conf`)

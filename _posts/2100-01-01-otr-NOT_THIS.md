---
layout: post
title: "Off-The-Record Messaging explained very clearly"
tags: [Security]
og_image: TODO-later
published: false
---
<style>
    img {
        image-rendering: -webkit-optimize-contrast;
    }
</style>

> “A dog ate my homework” is a much more credible excuse if you ostentatiously purchased twenty ferocious dogs the day before.*

#### Index

* [Part 1: the problem with PGP](/otr1)
* [Part 2: deniability and forward secrecy](/otr2)
* [Part 3: how OTR works](/otr3)
* [Part 4: OTR's key insights](/otr4)

## 0. Introduction 

Suppose that you want to have a clandestine conversation with a friend in a park. If you secure any nearby shrubberies then you can be confident that no one will be able to eavesdrop on you. And unless you're being secretly recorded or filmed you can be similarly confident that no one will be able to make a permanent, verifiable record of your conversation. This means that you and your friend can have a private, off-the-record exchange of views. Local parks - and the physical world in general - have reasonably strong and intuitive privacy settings.

However, in the cyberworld these settings get more complex. An internet eavesdropper can't hide in the bushes, but they can hack your computer or intercept your traffic as it travels over a network. There's no record of most real-world conversations apart from the other person's word, but electronic messages create a papertrail, which can be both useful and incriminating. These differences between the fleshy and virtual realms don't necessarily increase or decrease net privacy, but they do change the threats and vectors that security- and privacy-sensitive people within them need to consider.

For example, in the physical world a brief lapse in communication security usually has limited consequences. It might allow a snooper to overhear a single conversation, or a disgruntled confederate to loosely retell, without proof, the details of a past discussion. However, in the cyberworld, brief lapses can be catastrophic and the consequences can be even worse than merely exposing confidential information.

Suppose that, as happens all too often, an attacker steals a dump of electronic messages and the secret key needed to decrypt them. The attacker will be able to open and read the previously-secret messages. To make matters worse, they may also be able to exploit the messages' encryption protocol to prove to the world that the stolen messages are real, preventing the victims from claiming that they are fakes that should be ignored. On top of all this, the attacker may even be able to use the compromised secret key to decrypt years worth of historical messages that were also encrypted using that same key.

Fortunately we can mitigate these problems. Getting hacked doesn't have to reveal all of your historical messages, and it doesn't have to inadvertently provide proof that stolen messages are real. There's much more to cryptography than just encrypting and decrypting messages, and the details matter. For example:

* How do the sender and receiver authenticate each other's identities?
* Where do encryption keys come from?
* What algorithms are used to encrypt and decrypt messages?
* What happens to keys once they've been used?
* Do the sender and receiver ever need to generate new keys? How often?

*Off-The-Record Messaging* (OTR) is a cryptographic protocol that aims to replicate the privacy properties of a casual, in-person conversation. Like most cryptographic protocols, the primary goal of OTR is to prevent an attacker from reading its messages. But on top of this it guarantees that if someone somehow does gain access to an OTR message then they won't be able to prove that it is real, and they certainly won't be able to decrypt and read reams of historical messages. Any fool with decades of experience in high-grade cryptography can design a communication protocol that is secure when things go right. OTR focuses on what happens when things go wrong.

OTR does all this using standard, off-the-shelf ciphers and algorithms, and its (relatively) simple genius is in how it arranges old tools in novel patterns. In order to understand the innovations of OTR we don't need to pore over pages of mathematical proofs. Instead we have to think precisely about the system-level ways in which familiar primitives are chained together. OTR inspired the first version of the Signal Protocol, used by the secure messaging app Signal, and learning how OTR works will invigorate your own cryptographic imagination too.

### 0.1 About this long blog post/short book

This long blog post/short book is based on [Borisov, Goldberg and Brewer 2004][otr-paper], the paper that first introduced OTR. It assumes very little prior knowledge of cryptography. It won't hurt to have prior experience with concepts like public and private keys and cryptographic signatures, but don't worry if you don't, we'll cover what you need to know. Whereas Borisov, Goldberg and Brewer had but 7 pages in an academic journal, we have as much space as we like in which to cover the background, clarify the details, and ponder the ways in which OTR intersects with the 2020 US Presidential Election.

----

## 1. Why use Off-The-Record Messaging?

Alice and Bob want to talk to each other online. However, their privacy is under threat from the evil Eve, who wants to find out what they are saying and manipulate the contents of their messages. Alice and Bob want to stop her and talk to each other securely. To do this, they need a cryptographic protocol.

The two most basic properties that Alice and Bob need from a protocol are confidentiality and authenticity. Confidentiality means that Alice and Bob's messages stay private and that Eve cannot read them. Authenticity means that Alice and Bob can be confident that they are talking to the right person and that Eve cannot spoof fake messages.

However, these aren't the only properties that they want. Suppose that Eve hacks into Alice and Bob's computers and steals their cryptographic keys. Even in this disaster scenario, Alice and Bob would like to ensure that Eve can't use their keys to read any past encrypted messages that she has intercepted. This property is called forward secrecy. They would also like to prevent Eve from being able to prove that any messages that she does somehow steal are genuine. It's bad if Eve leaks their messages to the press, but it's less bad if they can credibly deny that they are real. This property is called deniability.

The original OTR paper was provocatively titled "Off-the-Record Communication, or, Why Not To Use PGP". PGP is a widely-used and simple cryptographic protocol that provides good confidentiality and authenticity, but not perfect foward secrecy or deniability. OTR aims to address these shortcomings.

Since OTR began life as a challenge to PGP, we'll begin our study of OTR by analysing PGP's strengths and weaknesses. Then, with a working understanding of PGP under our belts, we'll see how OTR mitigates PGP's problems.

### 1.1 PGP

The PGP protocol can be used both to *encrypt* a message (which keeps it secret) and to *sign* it (which proves who wrote it). In short, when Alice wants to send a message to Bob, she first writes it in plaintext. She encrypts and signs it (more on which in a second) and sends the ciphertext and signature to Bob. When Bob receives Alice's message he decrypts it, verifies the signature, and reads it.

<img src="/images/otr/otr-0a.png" />

If Eve intercepts Alice's message on its way to Bob then she won't be able to read it, and thanks to the signature she won't be able to manipulate it without Bob noticing. This means that Alice and Bob can exchange secure messages over an insecure network.

Let's look at how this all works.

#### Asymmetric encryption

At its core PGP uses an *asymmetric cipher*, which is an encryption algorithm that uses one key for encryption and a different one for decryption. Before a person can receive PGP messages, they must first generate a pair of mathematically linked keys called a keypair. One of these keys is their private key, which they must keep secret and safe at all costs. The other is their public key, which they can safely publish and make available to anyone who wants it, even their enemies.

<img src="/images/otr/otr-0.png" />

Distributing public keys reliably can be surprisingly difficult, and there is a deep literature on the ways in which they can be distributed, trusted, and un-trusted. [I've written about these mechanisms elsewhere](https://robertheaton.com/2018/11/28/https-in-the-real-world/), but here we'll assume that Alice and Bob are able to safely retrieve and trust each other's public keys without problem.

The critical property of asymmetric encryption is that data encrypted with a person's public key can only be decrypted with their private key, and vice-versa.

<img src="/images/otr/otr-1.png" />

To see why this is so useful, suppose that Alice wants to send a secret message to Bob using an asymmetric cipher. The simplest way for her to do this is to directly encrypt her message using Bob's public key (although PGP does something different, as we'll see shortly). To do this, Alice retrieves Bob's public key and encrypts her message with it. She sends the resulting ciphertext to Bob, and Bob uses his private key to decrypt and read it.

<img src="/images/otr/otr-3.png" />

Since the message can only be decrypted using Bob's private key, which only Bob knows, Alice and Bob can be confident that Eve can't read their message even if she intercepts it.

#### Why is asymmetric encryption useful?

The big feature of asymmetric encryption is that it doesn't require Alice and Bob to agree on a shared key ahead of time. All they have to do is distribute their public keys. They don't care if Eve discovers them (so long as she doesn't also discover their private keys), and indeed they fully expect her to.

The opposite of asymmetric encryption is symmetric encryption. In symmetric encryption the same key is used for both encryption and decryption.

<img src="/images/otr/otr-9.png" />

In order to exchange messages using symmetric encryption, Alice and Bob have to first agree on the symmetric key that they will use. This is tricky, since they can't simply have one person generate a key and send it to the other. Eve might intercept the key and then use it to decrypt the messages that follow it. As we'll see, there do exist plenty of ways for Alice and Bob to agree on a shared, symmetric key without Eve being able to discover it, but doing this does require care.

Nonetheless, neither family of algorithms is inherently more "secure" than the other, and an attacker who doesn't know the relevant secret key will not be able to read a message that has been robustly encrypted with either type of algorithm.

#### How PGP uses asymmetric encryption

In fact, PGP uses both asymmetric and symmetric encryption. It does this because asymmetric encryption is slow, especially for long inputs. Using an asymmetric cipher to encrypt a long message in its entirety would be unacceptably time-consuming. By contrast, symmetric ciphers are much zippier. Alice and Bob would therefore prefer to do as much of their encryption and decryption as possible using a symmetric cipher instead of an asymmetric one. But how can they agree on a single, shared key to use with a symmetric cipher without Eve being able to see this key too?

PGP gets the best of both worlds with a neat trick. In PGP, Alice doesn't encrypt her entire message using an asymmetric cipher. Instead, she encrypts it using a symmetric cipher, with a random symmetric key that she generates called a session key.

To allow Bob to decrypt her message, Alice needs to send him the session key. She also needs to ensure that Eve can't read the key. To achieve this, she encrypts the session key using Bob's public key. Now Eve can't recover the session key without Bob's private key, which - all being well - only Bob knows. And since Eve can't recover the session key, she also can't decrypt Alice's actual message, even if she intercepts every byte of traffic that Alice and Bob exchange. Alice can therefore confidently send both the symmetrically-encrypted message and asymmetrically-encrypted session key to Bob.

<img src="/images/otr/otr-12.png" />

To read Alice's message Bob reverses Alice's process. He uses his private key to decrypt the symmetric session key, and then uses the session key to decrypt the actual message. With PGP Alice and Bob get the convenience of asymmetric cryptography with the speed of symmetric.

#### Cryptographic signatures

However, even though Bob is the only person who can read Alice's message, at the moment he has no proof that the message really was written by Alice. As far as he's concerned it could have been written and encrypted by Eve pretending to be Alice, or Eve could have intercepted and manipulated a real message from Alice. To prove to Bob that she wrote her message, Alice uses PGP to *cryptographically sign* it before sending it.

A cryptographic signature is a blob of data attached to a message that allows the recipient to prove to themselves who wrote the message. It also allows them to satisfy themselves that the message has not been tampered with. Signatures can be generated in several different ways, including the same kind of asymmetric cryptography that Alice and Bob just used to encrypt their messages.

When encrypting and decrypting a message using asymmetric cryptography, Alice and Bob exploit the fact that a message encrypted using a public key can only be decrypted using the corresponding private key. To sign a message, they exploit the equivalent but inverse fact that a message encrypted with a *private* key can only be decrypted using the corresponding *public* key.

<img src="/images/otr/otr-2.png" />

To produce a naive signature, Alice can take her encrypted message and encrypt it again using her private key. The result of this operation is the message's signature. She can attach this signature to her encrypted message and send both it and the message to Bob.

This signature is useful because Bob can decrypt it using Alice's public key, and verify that the result is equal to Alice's encrypted message. This proves to Bob that the signature was produced using Alice's private key, and therefore that the message was signed and written by Alice. He also knows that the message hasn't been tampered with in transit, because if it had then the result of decrypting the signature would no longer equal the encrypted message. In order to mess with the message without being detected, Eve would need to update the signature too. However, since she doesn't know Alice's private key, she can't generate a valid signature for her mutated message.

This is the principle underlying all types of cryptographic signature.

#### Cryptographic signatures in practice

In practice, Alice doesn't actually sign her encrypted message directly. This is because, as we know, asymmetric encryption is slow. On top of this, signing the entire message would produce a signature of the same length as the message, which would require unnecessary bandwidth to send. What's more, short messages would produce short signatures, which could be easy for an attacker to forge, even without knowing Alice's secret key.

Alice therefore starts by passing her message through a *hash function*, which is an algorithm that produces a random-seeming but consistent and fixed-length output for a given input. She then signs the output of the hash function with her private key.

<img src="/images/otr/otr-5a.png" />
<img src="/images/otr/otr-5b.png" />

Putting this all together gives us the following picture:

<img src="/images/otr/otr-4.png" />

When Bob receives Alice's message and signature, he uses a hash function to verify the signature too. He decrypts Alice's signature using her public key, but then instead of comparing the result to her message directly, he first hashes her message and compares the output to the decrypted signature. If they match then Bob can be confident that the message is authentic.

### The problems with PGP

Encryption and signatures are how PGP gives Alice and Bob confidentiality and authenticity. We've seen how Eve can't decrypt Alice's messages because she doesn't know Bob's private key, and so she can't decrypt the symmetric session key. She can't spoof a fake message from Alice to Bob because she doesn't know Alice's private key, and so won't be able to generate a valid signature. If everything goes perfectly, PGP works perfectly.

However, in the real world, we also have to plan for the times when everything does not go perfectly. This is where PGP falls down, and where OTR aims to improve on it. PGP relies heavily on private keys staying private. If a user's private key is stolen (for example, if their computer is hacked and all their files stolen) then the security properties previously underpinned by it are blown apart. Suppose that Eve steals a copy of Bob's private key and intercepts Alice's message on its way to Bob. She'll be able to decrypt the session keys that Alice encrypts using Bob's public key, and then use them to decrypt Alice's messages. If she steals a copy of Alice's private key then she can use it to sign fake messages that Eve herself has written, making it look like these messages came from Alice.

All encryption is to some degree underpinned by the assumption that secret keys stay secret, and so we should expect any protocol to be severely damaged if this assumption is broken. But with PGP the fallout is worse than just leaking confidential messages. We know already that if Eve steals a private key then she can use it to decrypt any future PGP messages that she intercepts and that were encrypted using the corresponding public key. But suppose that Eve has been listening to Alice and Bob for months or years, patiently storing all of their encrypted traffic. Previously she had no way to read any of this traffic, but with access to Bob's private key she can now decrypt all of their historical session keys and use them to decrypt all of their old, previously-secret messages.

But it gets *even* worse. Alice cryptographically signed all her PGP messages so that Bob could be confident that they were authentic. However, whilst generating a signature requires Alice's private key, verifying it only requires her public key, which is typically freely available. This means that Eve can use Alice's signatures to verify the authenticity of messages that she steals from Bob just as well as Bob can. If Eve gets access to Alice and Bob's signed messages, she also gets access to a cryptographically verifiable transcript of their communications. This prevents Alice and Bob from credibly denying that the stolen messages are real. In a few sections' time we'll look at some real-world examples of how cryptographic signatures like this can cause serious problems for the victims of hacks.

PGP does give confidentiality and authenticity. But it's brittle, and it isn't robust to private key compromise. We'd ideally like an encryption protocol that better mitigates the consequences of a hack. In particular we'd like two extra properties. First, we'd like *deniability*, which is the ability for a user to credibly deny that they ever sent hacked messages. And second, we'd like *forward secrecy*, which is the property that if an attacker compromises a user's private key then they are still unable to read past traffic that was encrypted using that keypair.

Let's examine these properties in detail and see why they are so desirable. Then we'll look at how Off-The-Record-Messaging achieves them.

### 1.2 Deniability

Deniability is the ability for a person to credibly deny that they knew or did something. It's one of the main focusses of OTR, but one of the main weaknesses of PGP.

Statements from in-person conversations are usually easily deniable. If you claim that I told you that I robbed a bank then I can credibly retort that I didn't and you can't prove otherwise.

Email conversations can be deniable too (although see below for a look into why in practice they often aren't). Suppose that you forward to a journalist the text of an email in which I appear to describe my plans to rob a hundred banks. I can credibly claim that you edited the email or forged it from scratch, and you still can't prove that I'm lying. The public or the police or the judge might believe your claims over mine, but nothing is mathematically provable and we're down in the murky world of human judgement.

By contrast, we've seen that PGP-signed messages are not deniable. If Alice signs a message and sends it to Bob then Bob can use the PGP signature to validate that the message is authentic. However, all this validation requires is Alice's public key, which is freely available. This means that anyone else who comes into possession of the message can also validate the signature and prove that Alice sent the message in exactly the same way that Bob did. Alice is therefore permanently on the record as having sent these messages. If Eve hacks Bob's messages, or if Alice and Bob fall out and Bob forwards their past communication to her enemies, Alice cannot plausibly deny having sent the messages in the same way as she could if she had never signed them. If you forward to a journalist a cryptographically signed email in which I describe my plans to rob a thousand banks, I will be in a pickle.

On the face of it, deniability is in tension with authenticity. Authenticity requires that Bob can prove to himself that a message was sent by Alice. By contrast, deniability requires that Alice can deny having ever sent that same message. As we'll see, one of the most interesting innovations of OTR is how it achieves these seemingly contradictory goals simultaneously.

Technically anything can be denied, even cryptographic signatures. I can always claim that someone stole my computer and guessed my password, or infected my computer with malware, or stole my private keys while I was letting them use my computer to look up the football scores. These claims are not impossible, but they are unlikely and tricky to argue. Deniability is a sliding scale of plausibility, and so OTR goes to great lengths to make denials more believable and therefore more plausible. "A dog ate my homework" is a much more credible excuse if you ostentatiously purchased twenty ferocious dogs the day before.

It's perfectly reasonable to believe that a deniable message is still authentic. We all assess and believe hundreds of claims every day using vague balances of probability, without mathematical proof. Screenshots of a WhatsApp conversation might reasonably be enough to convince the authorities of my plans to rob ten thousand banks, even without cryptographic signatures.

But as we'll now see, if signatures are available then that does make everything easier.

#### 1.2.1 DKIM, the Podesta Emails, and the Hunter Biden laptop

For message senders, deniability is almost always a desirable property. There's rarely any advantage to having everything you say or write go into an indelible record that might come back to haunt you. This is not the same thing as saying that deniability is an objectively good thing that makes the world strictly better. Just take the intertwined stories of the DKIM email verification protocol; US Democratic Party operative John Podesta; and the laptop of Hunter Biden, son of President Joe Biden.

In order to understand the politics of these stories, we first need to discuss the protocols. In the old days, when an email provider received an email claiming to be from `rob@robmail.com`, there was no way for the provider to verify that the email really was sent by `rob@robmail.com`. The provider therefore typically crossed their fingers, hoped that the email was legitimate, and accepted it. Spammers abused this trust to bombard email inboxes with forged emails. The DKIM protocol was created in 2004 to allow email providers to verify that the emails they receive are legitimate, and the protocol is still used to this day.

DKIM uses many of the same techniques as PGP. In order to use DKIM (which stands for *Domain Keys Identified Mail*), email providers generate a keypair and publish the public key to the world (via a DNS TXT record, although the exact mechanism is not important to us here). When a user sends an email, their email provider generates a signature for the message using the provider's private signing key. The provider inserts this signature into the outgoing message as an email header.

<img src="/images/otr/otr-7.png" />

When the receiver's email provider receives the message, it looks up the sending provider's public key and uses it to check the DKIM signature against the email's contents, in much the same way as a recipient would check a PGP message signature against a PGP message's contents. If the signature is valid, the receiving provider accepts the message. If it isn't, the receiving provider assumes that the message is forged and rejects it. Since spammers don't have access to mail providers' signing keys, they can't generate valid signatures. This means that they can't generate fake emails that pass DKIM verification, making DKIM very good at detecting and preventing email forgery.

But as we've seen with PGP, where there's a cryptographic signature, there might also be a problem with deniability. As well as providing authentication, a DKIM signature provides permanent, undeniable proof that the signed message is authentic. DKIM signatures are part of the contents of an email, so they are saved in the recipient's inbox. If a hacker steals all the emails from an inbox, they can validate the DKIM signatures themselves using the sending provider's public DKIM key, in the same way that the recipient's email provider did when it received the message. The attacker already knows that the emails are legitimate, since they stole them with their own two hands. However, DKIM signatures allow them to prove this fact to a sceptical third-party as well, obliterating the emails' deniability. Email providers change, or *rotate*, their DKIM keys regularly, which means that the public key currently in their DNS record may be different to the key used to sign the message. Fortunately for the attacker, historical DKIM public keys for many large mail providers can easily be found on the internet.

Matthew Green, a professor at Johns Hopkins University, [points out](https://blog.cryptographyengineering.com/2020/11/16/ok-google-please-publish-your-dkim-secret-keys/) that making emails non-repudiatable in this way is not one of the goals of the DKIM protocol. Rather, it's an odd side-effect that wasn't contemplated when DKIM was originally designed and deployed. Green argues that DKIM signatures make email hacking a much more lucrative pursuit. It's hard for a journalist or a foreign government to trust a stolen dump of unsigned emails sent to them by an associate of an associate of an associate, since any of the people in this long chain of associates could have faked or embellished the emails' contents. However, if the emails contain cryptographic DKIM signatures generated by trustworthy third parties (such as a reputable email provider), then the emails are provably real, no matter how questionable the character who gave them to you. Cryptographic signatures don't decay with social distance or sordidness. Data thieves are able to piggy-back off of Gmail's (or any other DKIM signer's) credibility, making stolen, signed emails a verifiable and therefore more valuable commodity. 

This causes problems in the real world. In March 2016, Wikileaks published [a dump of emails](https://wikileaks.org/podesta-emails/) hacked from the Gmail account of John Podesta, a US Democratic Party operative. Alongside each email Wikileaks published [the corresponding DKIM signature](https://wikileaks.org/podesta-emails/emailid/10667), generated by Gmail or whichever provider sent the email. This allowed independent verification of the messages, which prevented Podesta from claiming that the emails were nonsense fabricated by liars.

You may think that the Podesta hack was, in itself, a good thing for democracy, or a terrible thing for a private citizen. You may believe that the long-term verifiability of DKIM signatures is a societal virtue that increases transparency, or a blunder that incentivizes email hacking. But whatever your opinions, you'd have to agree that John Podesta definitely wishes that his emails didn't have long-lived proofs of their provenance, and that most individual email users would like their own messages to be sent deniably and off-the-record.

Matthew Green has a counter-intuitive but elegant solution to this problem. Google already regularly rotate their DKIM keys. They do this as a best-practice precaution, in case the keys have been compromised without Google realizing. Green proposes that once Google (and other mail providers) have rotated a DKIM keypair and taken it out of service, they should *publicly publish* the keypair's *private key*.

This sounds odd. Publishing an DKIM private key means that anyone can use it to spoof a valid-looking DKIM signature for an email. If the keypair were still in use, this would make Google's DKIM signatures useless. However, since the keypair has been retired, revealing the private key does not jeopardize the effectiveness of DKIM in any way. The purpose of DKIM is to allow *email recipients* to verify the authenticity of a message *at the time they receive that message*. Once the recipient has verified and accepted the message, they don't need to re-verify it in the future. The signature has no further use unless someone - such as an attacker - wants to later prove the provenance of an email.

Since DKIM only requires signatures to be valid and verifiable when the email is received, it doesn't matter if an attacker can spoof a signature for an old email. In fact it's desirable, because it renders worthless all DKIM signatures that were legitimately generated by the email provider using the now-public private key. Suppose that an attacker has stolen an old email dump containing many emails sent by Gmail, complete with DKIM signatures generated using Gmail's now-public private key. Previously, only Google could have generated these signatures, and so the signatures proved that the emails were genuine. However, since the old private key is now public, anyone can use it to generate valid signatures themselves. All a forger has to do is take the now-public private DKIM key of the email provider, plus the contents of the email that they want to sign. They use the key to sign the email, in much the same way as they would sign a PGP message. Finally, they add the resulting signature as an email header, just as the email provider would.

This means that unless an attacker with a stolen batch of signed emails can prove that their signatures were generated while the key was still private (which in general they won't be able to), the signatures don't prove anything about anything to a sceptical third party. This applies even if the attacker really did steal the emails and is engaging in only a single layer of simple malfeasance.

But how much difference does any of this really make? Wouldn't everyone have believed the Podesta Emails anyway, without the signatures? Possibly. But consider a more recent example in which I think that DKIM signatures could have changed the course of history, had they been available.

During the 2020 US election campaign, Republican operatives claimed to have gained access to a laptop belonging to Hunter Biden, son of the then-Democratic candidate and now-President Joe Biden. The Republicans claimed that this laptop contained gobs of explosive emails and information about the Bidens that would shock the public.

The story of how the Republicans allegedly got hold of this laptop is somewhat fantastical, winding by way of a computer repair shop in a small town in Delaware. However, fantastical stories are sometimes true, and this is exactly the type of situation in which cryptographic signatures could play a big role in establishing credibility. It doesn't matter how wild the story is if the signatures validate. Indeed, in an effort to prove the laptop's provenance, Republicans released a single email, with [a single DKIM signature](https://github.com/robertdavidgraham/hunter-dkim), that they claimed came from the laptop.

<img src="/images/otr/otr-8.png" />

The DKIM signature of this email is valid, and when combined with the email body (not shown above) it does indeed prove that `v.pozharskyi.ukraine@gmail.com` sent an email to `hbiden@rosemontseneca.com` about meeting the recipient's father, sometime between 2012 and 2015 (the period for which the DKIM signing key was valid). However, it also raises a lot of questions, and provides a perfect example of the sliding-scale nature of deniability.

The email doesn't prove anything more than what it says. It doesn't prove who `v.pozharskyi.ukraine@gmail.com` is (although other evidence might). It doesn't prove that there are thousands more like it, and it doesn't prove that the email came from the alleged laptop.

The email is cryptographically verifiable, but without further evidence the associated story is still plausibly deniable. I suspect that if a full dump of emails and signatures had been released, a la Wikileaks and Podesta, then their combined weight could have been enough to overcome many circumstantial denials. If the Republicans were also sitting on a stack of additional, also-cryptographically-verifiable material then it's hard to understand why they chose to release only this single, not-particularly-incendiary example. Maybe the 2020 election could have gone a different way. Cryptographic deniability is important.

----

You can't deny that we've studied deniability in depth, so now let's look at the other new property that Off-The-Record-Messaging provides: forward secrecy.

## 1.3 Forward Secrecy

Alice and Bob are once again exchanging encrypted messages over a network connection. Eve is intercepting their traffic, but since their messages are encrypted she can't read them. Nonetheless, Eve decides to store Alice and Bob's encrypted traffic, just in case she can make use of it in the future.

A year later, Eve compromises one or both of Alice and Bob's private keys. For many encryption protocols, Eve would be able to go back to her archives and use her newly stolen keys to decrypt all their encrypted messages that she has stored over the years. This would be a disaster. However, if Alice and Bob were using an encryption protocol with the remarkable property of *forward secrecy* then Eve would not be able to decrypt their stored historical traffic, even though she has access to their private keys.

Here's Wikipedia's definition of forward secrecy:

> Forward Secrecy is a feature of specific key agreement protocols that gives assurances your session keys will not be compromised even if the private key of the server is compromised. *([Wikipedia](https://en.wikipedia.org/wiki/Forward_secrecy))*

We've seen in part 1 [TODO-LINK] that PGP does not give forward secrecy. Suppose that Eve stores encrypted PGP communication and later compromises Bob's private key. Eve can now use Bob's private key to decrypt all of the historical session keys that Alice encrypted using Bob's public key. This means that she can use those session keys to decrypt all of Alice's corresponding messages, long after they were sent.

To prevent this from happening, Alice and Bob need a session key exchange process that prevents Eve from working out the value of the key, even if she watches all of their key-exchange traffic, and even if she compromises their private keys. The original version of OTR achieved this remarkable property using a key-exchange protocol called *Diffie-Hellman* (other similar protocols would also work), which we'll look at more later. 

To complete their guarantee of forward secrecy, Alice and Bob need to "forget" each session key as soon as they are done with it, wiping it from their RAM, disk, and anywhere else from which an attacker who compromises their computers might be able to recover it. If Alice and Bob agree their session keys using a carefully designed key-exchange protocol like Diffie-Hellman and fully forget them once they're no longer needed, then there is no way for anyone to work out what the values of those session keys were; even the attacker; and even Alice and Bob. There is therefore no way, in any circumstances, for anyone to decrypt traffic or encrypted message dumps that were encrypted using one of these forgotten session keys. Forward secrecy, and with it one of the primary goals of OTR, is achieved.

Forward secrecy is often called "perfect forward secrecy", including by many very eminent cryptographers. Other, similarly eminent cryptographers object to the word "perfect" because (my paraphrasing) it promises too much. Nothing is perfect, and even when a forward secrecy protocol is correctly implemented, its guarantees are not perfect until the sender and receiver have finished forgetting a session key. Between the times at which a message is encrypted and the key is forgotten lies a window of opportunity for a sufficiently advanced attacker to steal the session key from the participants' RAM or anywhere else they might have stored it. In practice the guarantees of forward secrecy are still strong and remarkable. But when discussing Off-The-Record Messaging, a protocol whose entire reason for existence is to be robust to failures, these are exactly the kinds of edge-cases we should contemplate. We'll talk about this more in later sections.

----

It's clear why confidentiality and authenticity are desirable properties for a secure messaging protocol. Confidentiality prevents attackers from reading Alice and Bob's messages, while authenticity allows Alice and Bob to be confident that they are each talking to the right person and that their messages have not been tampered with.

We've also seen why deniability and forward secrecy are important. Deniability allows participants to credibly claim not to have sent messages in the event of a compromise. This replicates the privacy properties of real-life conversation and makes the fallout of a data theft less harmful. Forward secrecy, the other property that we discussed, prevents attackers from reading historical encrypted messages, even if they compromise the long-lived private keys used at the base of the encryption process.

The goal of OTR is to achieve all of these properties simultaneously, and now we're ready to see how it does this. We'll start by looking at the broad mechanics of how an OTR exchange works, then we'll delve deeper into its subtler design decisions.

## 2. How does Off-The-Record Messaging work?

At a high level, an OTR exchange looks similar to that of many other encryption protocols.

In order to exchange an OTR message, the sender and recipient must:

<ol>
  <li><a href="#21-agreeing-on-an-encryption-key">Agree on a secret encryption session key</a></li>
  <li><a href="#22-verifying-identities">Verify each other's identities</a></li>
</ol>

Then the sender must:

<ol start="3">
  <li><a href="#23-encrypting-a-message">Encrypt the message</a></li>
  <li><a href="#24-signing-a-message">Sign the message</a></li>
  <li><a href="#25-sending-the-message">Send the message</a></li>
</ol>

And the recipient must:

<ol start="6">
  <li><a href="#26-decrypting-and-verifying-the-message">Decrypt the message and verify its signature</a></li>
</ol>

Then the sender must:

<ol start="7">
  <li><a href="#27-an-unexpected-twist-publishing-the-signing-key">Publish the previously-secret signing session key (yes, this is surprising)</a></li>
</ol>

Finally, the sender and recipient must both:

<ol start="8">
  <li><a href="#28-forgetting-the-encryption-key">Forget the encryption session key in order to preserve forward secrecy</a></li>
</ol>

This sounds straightforward enough, but OTR's fanatical desire for deniability and forward secrecy mean that there's a lot of nuance in those little bullet points. There are also a few extra steps that I've left out for now because they won't make much sense until we get there.

Let's start at the top.

### 2.1 [Agree on a secret encryption session key](#21-agreeing-on-an-encryption-key)

Alice and Bob start by agreeing on a shared, symmetric, ephemeral session key. They will later use this key to encrypt a message using a symmetric cipher. In order to preserve forward secrecy, once they have finished exchanging a message, they forget the session key that they used to send it and re-agree on a new one. The exact cadence at which they agree on new session keys is discussed in detail in [the original OTR paper][otr-paper], but for our purposes we can assume that session keys are rotated roughly every message.

<img src="/images/otr/otr-13.png" />

Alice and Bob securely agree on each shared secret key without allowing Eve to discover them by using a Diffie-Hellman key exchange, as briefly mentioned above. The guts of Diffie-Hellman are complicated and not necessary in order to explain OTR, but a broad understanding is still instructive.

#### 2.1.1 Diffie-Hellman key exchange

Roughly speaking, to begin a Diffie-Hellman key exchange Alice and Bob each separately choose a random secret number. They each send the other a specially-chosen intermediate number that is derived from, but isn't, their own random secret number. Now each knows their own random secret number, as well as the intermediate number that the other sent them. Thanks to the careful construction of the Diffie-Hellman protocol, each can use their own secret number and the other person's intermediate number to derive the same final, secret key, which they can use as their shared session key.

<img src="/images/otr/otr-14a.png" />

Even if Eve snoops on their communication and sees both of the intermediate numbers that they exchanged, this does not allow her to compute the final, secret key, because she doesn't know either of their initial random secrets.

Wikipedia has [a good analogy](https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange#General_overview) that uses paint instead of numbers, but if you don't get it then don't worry, the details aren't important to us. What matters is that Diffie-Hellman allows Alice and Bob to agree on a shared symmetric key in a way that gives them forward secrecy and prevents Eve from discovering the key.

### 2.2 [Verify identities](#22-verifying-identities)

We've described how Alice and Bob agree on a shared secret session key that they can use for symmetric encryption. However, we haven't yet considered how they can verify the identity of the person they've agreed that session key with. At the moment Eve could intercept and block all of Alice and/or Bob's traffic, and then spoof a separate Diffie-Hellman key-exchange with each person herself! Alice and Bob would each have agreed a shared secret, but with Eve instead of each other. Eve would be able to read their messages and spoof replies to them, and Alice and Bob would have no way of knowing what had happened. This is called a man-in-the-middle attack.

<img src="/images/otr/otr-15.png" />

Even though OTR doesn't use asymmetric cryptography to encrypt its messages, it does user it for identity verification. In their original paper ([Borisov, Goldberg and Brewer 2004][otr-paper]), the researchers who devised OTR recommended an elegant way in which Alice and Bob could use public/private keypairs to verify each other's identities when performing a Diffie-Hellman key exchange.

However, a few years later another paper ([Alexander and Goldberg 2007](https://www.cypherpunks.ca/~iang/pubs/impauth.pdf)) was published that described a weakness in this approach. The second paper proposed a broadly similar but more complex alternative. Here we'll discuss the original, if slightly flawed procedure, since it's simpler and is still a good illustration of the general principle of authenticating a key-exchange.

In the original OTR formulation, in order to prove their identities to each other, Alice and Bob each signed the intermediate Diffie-Hellman values that they sent to the other person. Then, when they received a signed intermediate value, they verified the signature against the other person's public key. If the signature didn't check out, they aborted the conversation. If it did, they could be sure that the secret value corresponding to this intermediate value was known only to the person who signed the intermediate value. They could proceed to combine the intermediate value with their own secret value in order to produce the shared symmetric secret key. The intention of this process was to allow Alice and Bob to each be sure that they were agreeing a shared secret with the right person.

<img src="/images/otr/otr-16.png" />

Eve could still intercept and try to tamper with Alice and Bob's traffic. However, she would't be able to get them to accept an intermediate Diffie-Hellman value derived from her own random secret, because she wouldn't be able to produce a valid signature. She therefore would't be able to trick them into negotiating an encrypted connection with her.

However, Alexander and Goldberg 2007 showed that Eve could still manipulate this type of key exchange in other ways. Eve could have Alice and Bob negotiate a connection with each other, but trick Bob into believing that he was talking to Eve when he was really talking to Alice. Eve wouldn't be able to actually read any messages, but this was nonetheless an unacceptable level of shennanigans to allow in an otherwise robust protocol.

OTR therefore now uses the more intricate approach outlined in Alexander and Goldberg 2007, in which Alice and Bob use vanilla Diffie-Hellman to set up an encrypted but unauthenticated connection, and then authenticate each other's identities inside that channel.

Astute readers may be surprised that OTR ever used signatures to verify participants' identities. Haven't we been saying that public/private key cryptographic signatures are the enemy of deniability? Have we forgetten John Podesta already?

However, Alice and Bob never sign their actual messages using their private keys. All they sign are their intermediate key exchange values, and all that these signatures prove is that Alice and Bob exchanged two random-looking numbers. They don't prove anything about the contents of Alice and Bob's messages, meaning that the substance of their conversations remain fully deniable.

This said, Alice and Bob do still somehow need to sign their messages in order to authenticate their contents and ensure that they aren't tampered with. We'll soon see how they manage to do this while preserving deniability.

For now, Alice and Bob have agreed on a shared, symmetric, ephemeral session key and verified each other's identities. Next, Alice needs to encrypt her message.

### 2.3 [Encrypt the message](#23-encrypting-a-message)

At this point, Alice and Bob have agreed on a secret, symmetric session key. We now need to specify a symmetric encryption algorithm (or *cipher*) that they can pass their key into in order to encrypt and decrypt their messages. Many such encryption algorithms exist already, and OTR can use a pre-existing algorithm without inventing its own.

For counter-intuitive reasons that we will discuss shortly, OTR requires a *malleable* cipher. A malleable cipher is one for which it is possible for an attacker to manipulate a ciphertext so that it decrypts to an alternative plaintext chosen by the attacker. This is usually a lousy property. For example, the attacker can tweak an encrypted message that decrypts to "Release the prisoner" into one that decrypts to "Execute the prisoner". This manipulated message will be decryptable using the symmetric key agreed by the sender and receiver, which means that the receiver will be inclined to believe that it is legitimate.

In order to exploit the cipher used by OTR, the attacker needs to be able to guess the plaintext that an original ciphertext decrypts to. The alternative plaintext that they want to produce must be the same length as the original. If they can make such a successful guess, the attacker can produce their new, seemingly-valid ciphertext without needing to know the keys that were used to encrypt or decrypt the original ciphertext.

Even though malleability is usually not a desirable property, we'll see later why it is oddly useful for OTR. OTR uses a malleable cipher called a "stream cipher with AES in counter mode", but the details of how this particular cipher works aren't important to us here.

Alice and Bob have now agreed on a key, verified each other's identities, and have an encryption cipher that they can use. They haven't used their private keys to sign anything important, which means that there's nothing cryptographically tying them back to their message in the event of a compromise. They are therefore ready to use their key and cipher to encrypt, exchange, and decrypt a message.

However, we haven't yet given Alice and Bob a way to detect whether their encrypted messages are tampered with in transit. The fact that a stream cipher is malleable, and therefore particularly easy to manipulate, makes this check especially important for OTR. Let's see how OTR authenticates the contents of its messages without jeopardizing Alice and Bob's ability to deny that they sent them.

### 2.4 [Sign the message](#24-signing-a-message)

In order to authenticate the contents of a message, the sender needs to be able to sign it and the receiver needs to be able to validate this signature. However, Alice and Bob don't want to sign their messages directly using their private signing keys (which is what PGP does), because this would make them un-deniable.

OTR therefore has to prove the integrity of its messages using a different type of cryptographic signature. We know already that OTR uses a symmetric encryption algorithm to encrypt its messages while preserving forward secrecy. Similarly, it also uses a symmetric *signing* algorithm to authenticate its messages while preserving deniability. Whereas an asymmetric signing algorithm (such as the one used by PGP) uses one key in a keypair to create a signature and the other key to verify it, a symmetric one uses the same key to both create and verify. We'll see why this is important shortly.

OTR uses a symmetric signing algorithm called HMAC, which stands for Hash-Based Message Authentication Code. In order to generate an HMAC signature for a message, the signer passes both their message and their symmetric, shared, secret signing key into the HMAC algorithm (we don't need to know any internal details about HMAC, but we'll talk about where this new secret key comes from in a few paragraphs' time). The algorithm returns an HMAC signature, and the signer sends the message and HMAC signature to the recipient.

<img src="/images/otr/otr-17.png" />

In order to verify an HMAC signature, the recipient performs the same process. They pass the message and the same signing key (which they also know) into the HMAC algorithm, and get back an HMAC signature. If the signature that they calculate matches the signature that they received from the sender then - assuming that the secret signing key has not been exposed - the recipient can be confident that the message has not been tampered with. This shows how HMAC signatures provide authentication, although it doesn't show how they preserve deniability. We'll come back to that in a few sections' time.

#### Agreeing on a symmetric signing key

In order to use HMAC signatures to authenticate their messages, the sender and recipient need to agree on a shared secret signing key that they can pass into the HMAC algorithm. In OTR they use the *hash* of their shared secret encryption key as their shared secret signing key.

<img src="/images/otr/otr-18.png" />

As mentioned several sections ago, a hash function is a function that produces a random-seeming but consistent output (often called simply a "hash") for each input. Given an input it is very easy to calculate the hash output. By contrast, given a hash output it is essentially impossible to calculate the input that produced it. In OTR Alice and Bob use a cryptographic hash function (a hash function with some specific security properties) to generate their shared signing key from their shared encryption key.

Using the hash of their encryption key as their signing key is convenient, since it removes the need for Alice and Bob to perform another key-exchange dance. It also provides a subtle contribution towards deniability that we will discuss later.

After a lot of preparation, Alice and Bob are finally ready to securely exchange a message.

### 2.5 [Send the message](#25-sending-the-message)

Alice encrypts her message using a stream cipher with AES in counter mode, plus the symmetric encryption key that she and Bob agreed using their Diffie-Hellman key exchange. She calculates the hash of the encryption key to give her their symmetric signing key. She hashes her encrypted message, and signs the hash using the HMAC algorithm plus the signing key. Lastly, she sends the message and signature to Bob.

### 2.6 [Decrypting and verifying the message](#26-decrypting-and-verifying-the-message)

Once Bob receives Alice's message he performs the same process in reverse. He decrypts the message using the shared encryption key. Like Alice, he calculates the hash of the encryption key to give him their symmetric signing key. Also like Alice, he hashes the encrypted message and re-calculates the signature using the HMAC algorithm and the shared signing key. He verifies that the signature he calculates matches the one that Alice sent him, hopefully proving that the message has not been tampered with. Alice and Bob have now exchanged a secret, authenticated, forward-ly-secret, and deniable message.

But there's more.

### 2.7 [An unexpected twist: publishing the signing key](#27-an-unexpected-twist-publishing-the-signing-key)

Penultimately and oddly, Alice *publishes* her and Bob's shared signing key to the world, for example by uploading it to a webpage that she controls. This is safe to do, because now that Bob has verified Alice's message, it doesn't matter if Eve has access to the signing key that he used to do this. This is the same principle by which it would be safe for Google to publish their private DKIM signing keys when they rotate them.

By contrast, it would be highly unsafe for Alice to publish their shared *encryption* key, because if Eve had stored their encrypted traffic then she would be able to use the encryption key to decrypt it. Happily, since the signing key that Alice publishes is only a cryptographic hash of the encryption key, it cannot be used to reconstruct the encryption key itself. All of this shows that publishing the signing key is a safe thing to do, but it doesn't say anything about why it's useful. We'll talk about this shortly.

### 2.8 [Forgetting the encryption key](#28-forgetting-the-encryption-key)

Finally, once Bob has received, decrypted, and verified a message, and Alice has published the private signing key, the participants forget and delete their session encryption key. As we've discussed, this step is necessary in order to preserve forward secrecy and to make it impossible for an attacker to ever penetrate their encrypted traffic, even if they compromise their computers. Alice and Bob then start the process again, negotiating a new shared session encryption key for each message.

Let's summarize these steps again:

1. Sender and recipient agree on a secret encryption session key using Diffie-Hellman key exchange.
1. They prove their identities to each other by signing the intermediate values in the Diffie-Hellman exchange
1. Sender uses the encryption key from step 1 to encrypt their message and signature
1. Sender signs their encrypted message using HMAC. They use a signing key equal to the cryptographic hash of the encryption key from step 1
1. Sender sends the encrypted ciphertext and signature to the recipient
1. Recipient decrypts the cipherext and verifies the accompanying signature
1. Sender publishes the HMAC key
1. Sender and recipient forget their session keys

That's how you send an OTR message, but it doesn't say much about why this fiddly foxtrot is useful. How exactly does it preserve deniability? Why does OTR use HMAC signatures? Why does it use a malleable cipher? And why on earth do participants publish their private signing keys once they're done with them?

Let's find out.

----

## 3. The key insights of OTR

### 3.1 Why does OTR use symmetric signatures instead of asymmetric ones?

OTR goes to a lot of trouble to use symmetric, HMAC signatures to authenticate its messages, instead of asymmetric ones. However, asymmetric signatures generated using public/private keypairs would also do a perfectly good job of authentication. Why does OTR bother with symmetric ones?

The answer is that symmetric signatures help preserve deniability. They help OTR avoid the Podesta problem, in which Wikileaks used (asymmetric) DKIM signatures to prove that the stolen dump of John Podesta's emails was legitimate.

Here's how symmetric signatures help with deniability. Remember, since HMAC signatures are symmetric, they are both created and verified using a single shared secret key that is known to both the signer and the verifier. The signer creates the signature by passing their message and the shared secret key into (in OTR's case) the HMAC signing algorithm. When a verifier needs to verify this signature, they do so by performing the same operation as the signer - using the same key - and making sure that their result matches the signature they were sent.

<img src="/images/otr/otr-17.png" />

Next, suppose that an attacker completely compromises Alice's computer. They steal a pile of messages that she has exchanged with Bob over OTR. The attacker wants to take the messages to Wikileaks and for Wikileaks to publish them. They know that Wikileaks will want cryptographic proof that the messages are real, so they also steal the messages' HMAC signatures. Since verifying an HMAC signature requires the shared signing key, the attacker uses their complete access to Alice's computer to steal these keys too, before Alice has a chance to wipe them from her RAM.

The attacker goes to Wikileaks and attempts to use the messages' HMAC signatures to prove that their stolen message dump is real. For each message they pass the message's contents and the HMAC secret into the HMAC algorithm. They demonstrate to Wikileaks that this signature matches the one in the stolen dump. For an asymmetric signature, this would be strong proof of the messages' legitimacy.

However, for a symmetric signature it doesn't prove anything! Since HMAC signatures are symmetric, the same key is used to both generate and verify them. Since the attacker necessarily needs to know this key in order to verify the signatures, they attacker could trivially have used the same key to forge the signatures themselves. They have no way to prove to Wikileaks that they didn't, even if they did in fact steal them fair and square. Note that the same logic could apply for asymmetric signatures if Wikileaks suspects that the attacker might have stolen Alice's private key and forged the signatures themselves.

This defence also works if Alice or Bob turns against the other and suddenly wants to expose their OTR communication to the world. They can publish all of the traffic, keys, signatures, and messages that they exchanged, but they can't prove that they didn't forge the signatures themselves. You might mostly trust your friends, but it's still good to use safe cryptography just in case.

The key difference between the symmetric and asymmetric signature scenarios is that asymmetric signatures are generated and verified using different keys. An attacker can therefore verify stolen signatures without having been able to generate them themselves. When attempting to use symmetric signatures to verify stolen messages, the attacker has *too much* power for their own good.

## 3.2 Why is it necessary and acceptable for OTR to sign its intermediate Diffie-Hellman values using asymmetric signatures?

We've been rattling on about how ingenious and important it is that OTR signs its messages using a symmetric algorithm and a shared secret key. This allows OTR to provide authentication while still preserving deniability. Alice and Bob can be confident that they are talking with each other directly, while also allowing them to deny that they ever spoke in the event that their communication is compromised.

However, the only reason that they are able to trust these symmetric signatures to provide authentication is that they trust that they agreed on the signing key that produced them with the right person. If an attacker were able to manipulate their key exchange process then they might be able to trick Alice into unwittingly agreeing a shared secret with them instead of Bob. The attacker would then be able to talk to Alice while impersonating Bob.

We been talking at great length about the deniability perils of asymmetric cryptography. But at some point, if you want to be sure that you're talking to the right person on the internet, you're probably going to have to use asymmetric signatures and public/private keypairs. In OTR Alice and Bob ensure that they are agreeing a key with the right person by using carefully-placed asymmetric signatures. How do these particular asymmetric signatures help, and why are they safe?

As we've seen, Alice and Bob agree on their shared symmetric encryption key using a Diffie-Hellman key exchange process. They later take the hash of this symmetric encryption key, and use this as their symmetric signing key. Importantly, they use asymmetric signatures to prove to the other person that they are agreeing these keys with the right person.

Recall that in a Diffie-Hellman key exchange, the participants each start by generating a long random number. They don't send each other these random numbers, but instead exchange carefully selected "intermediate values", derived from their original numbers. Thanks to some spectacular mathematics, by combining their own original number with the other party's intermediate value, both participants can generate the same shared secret key. Just as remarkably, even if an attacker intercepts their traffic and reads both of their intermediate values, the attacker will be unable to construct the shared secret key, since they don't know either of the original random numbers.

<img src="/images/otr/otr-14a.png" />

In order to give each other confidence that they are performing a Diffie-Hellman key exchange with the right person, Alice and Bob each sign their intermediate values using their private keys before sending them. When Alice and Bob receive the other person's intermediate value they can verify the accompanying signature using the other person's public key. This gives them confidence that the intermediate values were indeed generated by the right person, and therefore that they are performing a key exchange with the right person too. This means that they can trust that the shared secret derived from the key exchange is known only to them and the other person, and so any messages encrypted or signed using it and a symmetric algorithm (like HMAC) are real and unmolested.

Signing a Diffie-Hellman intermediate value with an asymmetric algorithm and a private key provides good authentication and trust in the resulting key, and doesn't impair participants' deniability. If an attacker intercepts the signed messages sent during key exchange then all they can prove is that Alice and Bob exchanged a few random numbers. This might help them build a circumstantial case that Alice and Bob have been exchanging covert messages, but Alice and Bob's cryptography doesn't mathematically incriminate them.

OTR provides strong authentication whilst preserving deniability by being very careful about what information it signs and how.

### 3.3 Why does the sender publish the shared HMAC signing key?

We've seen how HMAC signatures are used in OTR to provide "deniable authentication". But why on earth does the sender go to the effort of publishing their shared signing key to the world once they're done with it? The reason is similar, but subtly different, to the reason that Matthew Green called on Google to publish their DKIM signing secret keys several sections ago.

In OTR, a message signature doesn't need to provide everlasting proof of a message's authenticity to all people for all time. In fact, to preserve deniability, it's desirable that an OTR siganture provides proof of a message's validity to as few people as possible for as short a window as possible.

Only the recipient needs to be confident that an OTR message's signature is valid, and they only need to be confident of this when they are initially receiving the message and checking its signature. Once the recipient has used a signature to authenticate a message, they can record the fact that the message was valid. They need never look at the signature again, and they need never trust it again.

This means that once a recipient has used a signature to verify a message's validity, we want to make the signature as useless as possible to anyone who might steal it and who might want to use it to prove, or at least provide evidence, that the corresponding message is real. We want to blow the whole system up as soon as we're finished with it.

We've seen that OTR signatures are already close-to-useless to attackers because they are generated using the symmetric HMAC algorithm. An attacker can't ever use HMAC signatures to authenticate plundered messages to a sceptical third-party, because the third-party knows that the attacker could have trivially faked them. The attacker is in this predicament whether or not the participants publish their secret signing keys.

Nonetheless, the attacker can still use the HMAC signatures they've stolen to give themselves and their trusted accomplices additional confidence that the corresponding messages are genuine. From the attacker's point of view, the HMAC keys are known only to Alice, Bob, and the attacker. Since the attacker knows that they didn't fake the messages, they can be confident that they were legitimately written and signed by Alice and Bob, even though they can't cryptographically prove this to anyone else. If the attacker has accomplices who trust them implicitly then those accomplices can be similarly confident in the messages' veracity. For example, a court might trust an intelligence agency not to fake HMAC signatures, even though they could, and so take signatures as strong evidence of a message's genuineness.

However, by publishing their ephemeral HMAC signing keys, Alice and Bob make it harder for the attacker to be certain that their haul is genuine. If anyone can see their ephemeral HMAC signing keys, anyone could have written and signed the messages and snuck them onto Bob's hard drive. Admittedly, the most plausible explanation for how the messages got there is still that Alice and Bob wrote and signed them, but publishing their signing keys is still a cheap and cunning way for Alice and Bob to introduce some extra uncertainty and deniability into the mix. The attacker can't be as certain as they used to be that their stolen messages are real, and anyone that they share the messages with has to trust not only that the attacker is being honest (as before), but also that the messages weren't forged by a fourth-party. It's not an "I am Spartacus" moment so much as a "she is Spartacus, or maybe he is, or perhaps she is, I don't know, leave me alone."

### 3.4 Why does OTR use a malleable encryption cipher?

We've seen how OTR signatures are designed to crumble to dust when compromised by an attacker. However, it's possible for even an unsigned ciphertext to make tricky-to-deny ties back to its author. These ties aren't as mathematically bulletproof as a signature, but in the interests of completeness OTR tries to sever them by performing its encryption using a malleable, easy-to-tamper-with encryption cipher. How does this work?

The problem that the malleable cipher solves is that for most encryption ciphers it's hard to produce an encrypted ciphertext that decrypts to anything meaningful if you don't know the encryption key. It's not quite hard enough that you can assume that any ciphertext that decrypts to a sensible plaintext must have been generated by someone with access to the secret key, but it is still very hard. This means that if a ciphertext decrypts to sensible plaintext then it's reasonable to infer that it was probably generated by someone with access to the secret encryption key. This could give Eve good evidence that a message was sent by Alice or Bob, even without a useful signature.

To terminate this incomplete but still undesirable connection, OTR performs its encryption using a malleable stream cipher. A malleable cipher is one that makes it comparatively easy for an attacker to produce a ciphertext that decrypts to something sensible, even if they don't know the encryption key. The attacker does this by correctly guessing the plaintext that a stolen ciphertext decrypts to. If they guess correctly, the attacker can manipulate the stolen ciphertext so that it decrypts to any message of their choice of the same length.

<img src="/images/otr/otr-21.png" />

This tweakability gives Alice and Bob an extra layer of deniability, very similar to the one that they get from publishing their HMAC signing keys. Let's consider a scenario in which this layer might be useful. Suppose that Alice and Bob accidentally use a weak random-number generator (RNG) when choosing their random secret values at the start of their Diffie-Hellman key exchanges. This means that Eve is able to deduce the values of their random secrets by watching their key exchange traffic. She can use this information to work out their symmetric encryption keys, and use these keys to decrypt Alice and Bob's messages. This is already a bad outcome, but OTR's goal in disasters like this is to mitigate the mishap and make the revealed messages as deniable as possible.

Alice and Bob signed their messages using a symmetric HMAC session key, not their private keys. This means that Eve can't use their signatures as evidence that the messages are real. But even though Eve can't cast-iron prove anything, she can still try to build a case on-the-balance-of-probability. 

She can point out that Alice and Bob signed the intermediate values in their Diffie-Hellman key exchange using their private keys. Since they used a weak RNG to generate their secrets, Eve also knows their secret Diffie-Hellman values. She can use the asymmetric signatures on their intermediate Diffie-Hellman values to prove that Alice and Bob performed a key exchange that produced a specific symmetric session key. Eve can then use this session key to decrypt Alice and Bob's messages, and show that this produces sensible plaintexts. She then has suggestive evidence that Alice and Bob agreed on a particular session key, and then exchanged a message that could be successfully decrypted by this key.

We've discussed previously how this isn't a total deniability disaster, even without a malleable cipher. All it strictly proves is that Alice and Bob exchanged two random numbers, and there's no law against that. Symmetrically encrypted ciphertexts, even those encrypted using a non-malleable cipher, are just as useless for proving authorship as symmetrically signed messages. If Eve is able to decrypt a symmetrically encrypted ciphertext then she must have been able to forge that ciphertext. Eve therefore can't use Alice and Bob's ciphertexts to prove to other people that they wrote them, because Eve could have produced the ciphertexts herself.

However, as with HMAC signatures, the fact that the ciphertexts decrypt to a sensible plaintext does give Eve herself a lot of confidence that the messages are genuine, as well as anyone else who implicitly trusts Eve. If Eve knows that the symmetric encryption key was known only to Alice, Bob, and herself, and she knows that she didn't produce the ciphertext, then she knows that Alice or Bob must have.

To solve a similar problem with their HMAC signatures, Alice and Bob injected some extra ambiguity by publishing their HMAC signing keys after they had been used. This made it clear that anyone could have generated the signatures, not just Alice, Bob, or Eve. Eve could still assume that the signatures were probably generated by Alice or Bob, but now she also has to account for the increased possibility, however slight, that they were forged by a fourth-party.

Similarly, by using a malleable cipher, Alice and Bob make it more plausible that a ciphertext that can be legibly decrypted using their symmetric encryption key could also have been produced by a fourth-party, even if this fourth-party didn't know the key. All that this fourth-party would have had to do is intercept one of their real encrypted messages, correctly guess its plaintext version, and exploit the malleability of the stream cipher used to generate it. This isn't trivial, but it's much easier than if Alice and Bob used a more robust, non-malleable cipher.

Even though stream ciphers are easier to tamper with than many other types of cipher, OTR participants are protected from their messages being secretly tampered with by their HMAC signatures. If an attacker who doesn't know their encryption session key tampers with a message (perhaps by exploiting the malleable stream cipher as described above) then the HMAC signature will no longer be valid. The participants will know that they are under attack.

Despite these mitigations, if the attacker discovers their encryption (and therefore also their signing) keys then they then their privacy is still unavoidably obliterated. The attacker will be able to forge messages and signatures until the session keys expire. The best that OTR can do is to rotate session keys quickly and preserve as much deniability as possible, using all of the tools described above.

### 3.5 Why is the hash of the encryption key used as the signing key?

Alice and Bob use a Diffie-Hellman key exchange to agree on a symmetric encryption key. They could use a second Diffie-Hellman key exchange to agree on a symmetric signing key, but they don't. Instead, they calculate the hash of their encryption key, and use the result as their signing key.

<img src="/images/otr/otr-18.png" />

Linking encryption and signing keys in this way provides an interesting perk. It means that an attacker who compromises an encryption session key necessarily also compromises the corresponding signing key, whether they like it or not. All they need to do to derive the signing key is to take the hash of the stolen encryption key.

Oddly, this extra exposure benefits Alice and Bob. Suppose that an attacker is able to compromise a symmetric encryption key (perhaps becasue of a weak RNG in their key exchange) and read a message and signature. Because the signing key is just the hash of the encryption key, the attacker necessarily compromises the signing key as well. This means that it is impossible to have a situation where an attacker can decrypt a message, but can't forge a signature for it.

This makes it even harder for an attacker to steal messages and prove their validity to a third-party. The attacker could claim that they've never read [Borisov, Goldberg and Brewer 2004][otr-paper] and so they didn't know that they could use a stolen encryption key to derive the corresponding signing key, but if they've got this far in their attack then this would be hard to believe.

### 3.6 The Principle of Most Privilege

You may have heard of the Principle of Least Privilege. This widely-applied security precept states:

> Any user, program, or process should have only the bare minimum privileges necessary to perform its function.

Applying Least Privilege to your system means that an attacker who compromises one part of it won't be able to easily pivot into new parts and powers, and will therefore only be able to do limited damage. This is why spies operate in small cells; if they are discovered and interrogated then they don't have enough knowledge or privileges to help their captors roll up their chain of command. This is also why you shouldn't give everyone in your company administrator access to all of your systems. You might trust all your employees without reservation, but giving a user unnecessary powers needlessly worsens the consequences if they get hacked. It's bad if an attacker is able to read all of one person's emails; it's much worse if they can download everyone's emails, delete them all, and forge new messages that they look like they came from the CEO.

Nonetheless, I would argue that OTR goes out of its way to achieve the opposite: The Principle of Most Privilege! Whereas the goal of the Principle of Least Privilege is to minimize the power gained by an attacker who compromises one part of a system, the goal of the Principle of Most Privilege is to give an attacker who compromises one part of a system total power over all of it.

To see why this is oddly desirable for OTR, consider that the worst-case situation that OTR tries to prevent at all costs is the one in which an attacker:

1. Has access to an unencrypted message and a signature
2. Can prove to a sceptical third-party that the signature is valid
3. Could *not* have produced the signature themselves

This combination is a particular disaster because it means that the attacker can read Alice and Bob's messages, *and* prove their legitimacy to a sceptical third-party. It's important that the attacker can prove that a signature is valid (point 2), but *couldn't* have produced the signature themselves (point 3). This proves to the third-party that the attacker didn't forge the signatures themselves. The attacker benefits from their limitied capabilities, which is Least Privilege in action but in an oddly unhelpful way.

As we've seen, OTR prevents these 3 properties from occurring simultaneously by making it impossible for points 2 and 3 to be true at the same time. If an attacker can prove that a signature is valid (point 2) then they must be in possession of its symmetric HMAC key and so *could* have produced it themselves (the opposite of point 3). This is the Principle of Most Privilege - if you want to verify signatures, then you also have to be able to create them, whether you want this power or not. Usually we want to segment powers and credentials as much as possible; OTR is an odd situation in which we don't.

NB: whilst I do think that the Principle of Most Privilege is a useful lens through which to view OTR, it is not a real principle and I made it up. Don't bother Googling it.

----

## 4. Summary

We all hope that our communications stay secret and that we never get hacked. Unfortunately, sometimes we will. Any sensible encryption scheme is secure when everything goes as planned. OTR focusses on what happens when it doesn't.

OTR provides the standard properties of encryption and authentiction, plus the more subtle ones of deniability and forward secrecy. If your keys are compromised then Diffie-Hellman key exchange keeps your past messages safe. If your signatures are stolen then a symmetric signing algorithm mean that the attacker can't use them to prove the messages' validity to a third-party. Even if you use a weak random-number generator for your key exchange, OTR catches you with backup layers of deniability like a deliberately malleable encryption algorithm.

Admittedly, when we say that your messages are deniable and the attacker can't prove that you wrote them, we are using a narrow, mathematical definition of the word "prove". No matter how many cryptography papers you cite in your defence, the attacker might still be able to convince a newspaper or a jury on the balance of probabilities. But it's still useful to prevent your cryptography from actively working against you.

OTR weaves the strands of its protocol together in a deliberately fragile web. Signatures depend on encryption depend on key-exchanges, exploiting the Principle of Most Privilege (remember, not a real principle) to prevent an attacker from stealing signed messages that they could not have forged themselves. OTR forces us to think rigorously about what we mean by words like "authenticate" and "deny". Authenticate to who? When?

I hope OTR has sparked your cryptographic imagination as much as it has mine.

[otr-paper]: https://otr.cypherpunks.ca/otr-wpes.pdf
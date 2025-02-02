---
title: "I'm a security engineer and I still almost got scammed"
layout: post
tags: [Security]
og_image: https://robertheaton.com/images/scam-cover.png
---
I was in the park with my son and his best friend. I saw 2 missed calls from a number I didn’t recognise. I Googled it - it was my bank. I told the other adults that I should call back in case it was important.

<img src="/images/scam-cover.png" />

This was mistake number 1. Nothing the bank might want to talk about could be urgent enough to interrupt an unseasonably sunny March afternoon.

I got through to the bank, but they couldn’t work out why they had called me. I assumed that my credit card was being used for fraud and their systems were a mess. I made a note to check my account when I got home.

Ten minutes later I got another call from an anonymous number. I should have ignored it, but it was probably the bank and I wanted to get this fraud squared away without phone menus and hold music. I picked up, which was mistake number 2.

“Is this Robert Heaton?” a man said. “Who is this?” I said. “This is Barry from the fraud department at Bank Co,” he said. “I’m calling about some suspicious transactions on your account ending in 1234. Is this a good time to talk?”

I knew that I should hang up and call the number on the back of my card, tomorrow. Even though Barry knew my name, phone number, and account number, this didn't prove that he worked at Bank Co. This information is presumably freely available from any of the poorly-secured online retailers that I frequent. But it was still suggestive, especially given the earlier missed calls, and I'm busy and lazy and we were here already and I can handle myself. I wouldn't tell him any new details, but hopefully all I needed to say was "yes" and "no" and my problems would go away.

This was all an extension of mistake number 2.

“Did you recently authorise a transaction for £1,050.99 at the Apple Store in Manchester?” Barry asked. 

“No”, I said. 

He asked some more questions. “Did you give your card to a family member?” “Did you recently receive a text message from someone claiming to be the Post Office?” He paused for a long time in between each question; I answered no to them all.

“I’ve cancelled that charge and sent a new card out to you,” said Barry. “I’d like to enable enhanced security on your account, but I’ll need to text you a confirmation code first. Is that OK?” I wasn't happy about having to actively participate, but by now I'd been on the call for 10 minutes and didn't want to back out now. I decided to see where this was going. Barry sent me a text. It came from a new phone number, not the one that my bank uses for their other confirmation codes.

I was suspicious, but the bank's systems could easily be a wasteland archipelago of isolated micro-services that used different phone lines. Still, “I don’t have any proof of who you are,” I pointed out. “OK, I can send you another text confirming my name," he said. "That still doesn't really prove anything," I said. "I can also tell you the address that we’re sending the new card to?” he said.

Knowing my address would be suggestive, but nothing more. A lot of internet storekeeps who haven't changed their default passwords know my address too. “Can you tell me about any recent payments on the account?” I asked. “I’m sorry, I’m only able to see this one transaction,” he said. I knew I really should hang up now, but I wanted to get the £1000 charge off my plate and didn't want to have to go through this again tomorrow. “Can you tell me if there are any other people on the account?” I asked. He ignored me. “I’ve sent you a follow-up text message with my name and the case number.” My phoned buzzed again.

According to another text sent from the same number as the confirmation code, the man's name was indeed Barry and the case number was 2156291. Of course, anyone can make up a name and a case number. But I decided - incorrectly - that even if Barry was a scammer, his second message at least proved that he controlled the phone number that had sent the original code. I didn't see any harm in reading him back his own digits, so I did. This reasoning was wrong (see below), but fortunately I didn't get punished for it.

Next Barry said that he would need to deactivate my ApplePay. I don’t use ApplePay, but this still made sense to me. A year earlier I had requested a replacement card, and after sending it my bank had emailed me to say that they would transfer my ApplePay details over to the new card. Since I don’t use ApplePay, this worried me, so I called them up. The bank said that as far as they could tell no one had ever used my card with ApplePay, and they didn't know why they had sent me that email. They conjectured that maybe they send it to everyone, and it really meant “if you use ApplePay, we will transfer your card over.” Their systems sounded like a mess, but they told me not to fret.

Back in the present it sounded like someone actually had tried to add my card to ApplePay and now Barry was tidying up this loose end. My trust in him increased a little. Barry said he’d have to send me another confirmation code. “Why?” I asked. “I already confirmed my number once. And you called me!” “That’s how the system works,” Barry said. Silly but plausible, you know how banks are.

I got another text, this time from the normal number that my bank uses to send me one-time codes. `Your one-time verification code to add your card to Apple Pay is 123456`, it said. “It says that this is the code to add ApplePay, not remove it,” I said. “Uh, that must be a system error,” said Barry. “I can assure you, this is the code to remove ApplePay. Could you read it out to me?” “I’m not giving you this code,” I said. “That’s fine, but...if you don't then the money might leave your account any moment.” So this had all been a ruse. “I'll take my chances,” I said. I hung up and went back to my friends and family.

When I got home and checked there were no fraudulent charges, obviously. I called my bank and told them the whole story. The woman listened patiently for several minutes, then said that she would send me a new card. As far as I could tell she didn't take down any details.

---

I suspect that someone hacked a website where I'd bought a blanket or a bike helmet. This gave the attacker my name, address, phone number, and card number (known in the industry as my "fullz"), which they sold to Barry. However, Barry couldn’t use my card to buy anything online because my bank sends me a one-time verification code whenever I use the card on a new website.

So Barry called me up. He began with fifteen minutes of misdirection designed to lower my guard and get me invested in not having to go through this again. He stalled deliberately, pretending to check non-existent systems (while probably doing some villainous admin work) and empathising with how annoying it is to have to talk to your bank. He even sent and asked me to repeat a fake confirmation code in order to get me comfortable reading text messages back to him.

Once he had primed me as best he could he entered my card details into ApplePay and tried to trick me into telling him the real confirmation code that my bank then sent me. If I had given him this code then my card would have been added to his ApplePay wallet. He would have been able to use his phone for in-person contactless payments on my card, which wouldn't require verification codes. He might even have been able to use my card for online payments without needing any codes; I can't tell from the documentation. Fortunately I caught myself before we got that far.

I'm not sure where the 2 missed calls from my bank's real phone number came from. They made me much more credulous that Barry was legitimate, and if they were part of Barry's plan to lower my guard then they were a dainty touch. The internet tells me that caller IDs are easy to spoof, which I didn't know but doesn't surprise me. I'd guess that either Barry faked his caller ID, or the bank really did call a few times to offer me a higher credit limit and Barry got lucky.

A lot of the credit that I gave Barry came from my lack of faith in my bank's systems and security. I'm not sure this was fair of me, now that I think about it; I've been generally impressed with my bank's processes in the past. But I still have a justifiably low opinion of consumer security in general, and it seems that this bleeds into companies who are actually doing quite well. Insecure business practices often don't stand out as a sign of a con; they just look like another boneheaded but authentic policy.

Optimistically I don’t think I would have ever fallen for this particular coup de grace, but I still consider this interaction a disaster. I spent fifteen minutes dancing around my personal details with a scammer - a dangerous waste of time - and read Barry back the first confirmation code. I'm now certain that he did send me this code himself, but he could easily have had an accomplice on the phone with my real bank who could have triggered the bank to send a real code to me.

I like to think that I’m scam-savvy. I work as a "security engineer" at one of the larger financial tech companies, and my hobby is [writing about digital security](https://robertheaton.com/bumble-vulnerability/). [I nearly got spear-phished a few years ago](https://robertheaton.com/2019/06/24/i-was-7-words-away-from-being-spear-phished/) and I thought I'd learned a few lessons from that. I try to play a defensive but pragmatic game that allows me to stay safe while also successfully transacting with clumsy companies whose legitimate policies seem like hoaxes. “Could you please read out the 16-digit number on the front of the card? Yes we do have alternative payment methods, you can mail us cash or a cheque. OK, and now the expiry date?” But I'm still vulnerable, and I think I got lucky that I wasn't a notch more distracted and Barry's story wasn't a little more convincing.

With time to think and nothing else to do I can probably spot most consumer-grade scams, but under pressure and trying to cut corners I still blundered several times before I realised I was being had. Everyone makes mistakes, and security engineers need to design systems that are resilient to them. Even so, as a first line of defence you're never too experienced to follow the simple advice that you give everyone else.  Hang up and call back.
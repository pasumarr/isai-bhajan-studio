import os

bhajans = [
    {"title": "Ganesha Sharanam", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Adi", "lyrics": "Ganesha Sharanam Ganesha Sharanam<br/>Parama Pavanam Sadguru Sharanam", "audio_url": "/audio/ganesha_sharanam.mp3"},
    {"title": "He Shiva Shankara", "deity": "Shiva", "raga": "Bhairavi", "beat": "Keherwa", "lyrics": "He Shiva Shankara He Shiva Shankara<br/>Ganga Dhara Hara He Parameshvara", "audio_url": "/audio/he_shiva_shankara.mp3"},
    {"title": "Devi Bhavani Maa", "deity": "Devi", "raga": "Durga", "beat": "Keherwa", "lyrics": "Devi Bhavani Maa Devi Bhavani Maa<br/>Jagadamba Bhavani Maa Durga", "audio_url": "/audio/devi_bhavani_maa.mp3"},
    {"title": "Rama Nama Payasam", "deity": "Rama", "raga": "Anandabhairavi", "beat": "Adi", "lyrics": "Rama Nama Payasam Aa Aa<br/>Krishna Nama Sakkare Vitthala", "audio_url": "/audio/rama_nama_payasam.mp3"},
    {"title": "Govinda Krishna Jai", "deity": "Krishna", "raga": "Yaman", "beat": "Dadra", "lyrics": "Govinda Krishna Jai Govinda Krishna Jai<br/>Gopika Vallabha Roopini Jai", "audio_url": "/audio/govinda_krishna_jai.mp3"},
    {"title": "Sai Maa Jagadamba", "deity": "Sai", "raga": "Yaman", "beat": "Keherwa", "lyrics": "Sai Maa Jagadamba Sai Maa Jagadamba<br/>Janani Sathya Sai Maha Devi", "audio_url": "/audio/sai_maa_jagadamba.mp3"},
    {"title": "Sri Ganesha Vinayaka", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Roopak", "lyrics": "Sri Ganesha Vinayaka Sri Ganesha Vinayaka<br/>Parvati Nandana Siddhi Vinayaka", "audio_url": "/audio/sri_ganesha_vinayaka.mp3"},
    {"title": "Shankara Sadashiva", "deity": "Shiva", "raga": "Darbari", "beat": "Adi", "lyrics": "Shankara Sadashiva Shankara Sadashiva<br/>Kailasa Vasi Chandrashekhara", "audio_url": "/audio/shankara_sadashiva.mp3"},
    {"title": "Janani Maa Durga", "deity": "Devi", "raga": "Bhupali", "beat": "Keherwa", "lyrics": "Janani Maa Durga Janani Maa Durga<br/>Simhavahini Durga Bhavani", "audio_url": "/audio/janani_maa_durga.mp3"},
    {"title": "Raghupati Raghav Raja Ram", "deity": "Rama", "raga": "Mishra Kafi", "beat": "Keherwa", "lyrics": "Raghupati Raghav Raja Ram Raghupati Raghav Raja Ram<br/>Patita Pavana Sita Ram", "audio_url": "/audio/raghupati_raghav.mp3"},
    {"title": "Radhe Govinda Gopala", "deity": "Krishna", "raga": "Yaman", "beat": "Dadra", "lyrics": "Radhe Govinda Gopala Radhe Govinda Gopala<br/>Bhaja Mana Panduranga Vitthala", "audio_url": "/audio/radhe_govinda_gopala.mp3"},
    {"title": "Sai Baba Bolo", "deity": "Sai", "raga": "Mishra Pilu", "beat": "Keherwa", "lyrics": "Sai Baba Bolo Sai Baba Bolo<br/>Sathya Sai Baba Mukunda Hare", "audio_url": "/audio/sai_baba_bolo.mp3"},
    {"title": "Jai Jai Hanuman", "deity": "Hanuman", "raga": "Bhupali", "beat": "Keherwa", "lyrics": "Jai Jai Hanuman Jai Jai Hanuman<br/>Pavanaputra Sankat Haran", "audio_url": "/audio/jai_jai_hanuman.mp3"},
    {"title": "Ganesha Sharanam Parama Pavanam", "deity": "Ganesha", "raga": "Jog", "beat": "Keherwa", "lyrics": "Ganesha Sharanam Parama Pavanam Ganesha Sharanam Parama Pavanam<br/>Sadguru Sharanam Bhava Bhaya Haranam", "audio_url": "/audio/ganesha_sharanam_parama_pavanam.mp3"},
    {"title": "Shiva Shiva Shambho", "deity": "Shiva", "raga": "Shivaranjani", "beat": "Adi", "lyrics": "Shiva Shiva Shambho Shiva Shiva Shambho<br/>Hara Hara Shankara Mahadeva", "audio_url": "/audio/shiva_shiva_shambho.mp3"},
    {"title": "Amba Parameshwari", "deity": "Devi", "raga": "Kalyani", "beat": "Adi", "lyrics": "Amba Parameshwari Amba Parameshwari<br/>Akhilandeswari Rajeshwari", "audio_url": "/audio/amba_parameshwari.mp3"},
    {"title": "Sri Rama Chandra Kripalu", "deity": "Rama", "raga": "Yaman", "beat": "Adi", "lyrics": "Sri Rama Chandra Kripalu Sri Rama Chandra Kripalu<br/>Bhaju Mana Harana Bhava Bhaya", "audio_url": "/audio/sri_rama_chandra_kripalu.mp3"},
    {"title": "Hari Bolo Hare Krishna", "deity": "Krishna", "raga": "Bhupali", "beat": "Keherwa", "lyrics": "Hari Bolo Hare Krishna Hari Bolo Hare Krishna<br/>Gopala Hari Govinda Bolo", "audio_url": "/audio/hari_bolo_hare_krishna.mp3"},
    {"title": "Love Is God", "deity": "Sai", "raga": "Mixed", "beat": "Keherwa", "lyrics": "Love Is God Love Is God<br/>Live In Love And Be Peaceful", "audio_url": "/audio/love_is_god.mp3"},
    {"title": "Anjaneya Veera", "deity": "Hanuman", "raga": "Madhyamavati", "beat": "Adi", "lyrics": "Anjaneya Veera Anjaneya Veera<br/>Sankata Harana Maruthi", "audio_url": "/audio/anjaneya_veera.mp3"},
    {"title": "Vighneshvara Vinayaka", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Keherwa", "lyrics": "Vighneshvara Vinayaka Vighneshvara Vinayaka<br/>Gajanana Hey Shubhanana", "audio_url": "/audio/vighneshvara_vinayaka.mp3"},
    {"title": "Om Namah Shivaya", "deity": "Shiva", "raga": "Bhairavi", "beat": "Keherwa", "lyrics": "Om Namah Shivaya Om Namah Shivaya<br/>Shiva Shiva Shankara Hara", "audio_url": "/audio/om_namah_shivaya.mp3"},
    {"title": "Durge Devi Namo Namah", "deity": "Devi", "raga": "Durga", "beat": "Keherwa", "lyrics": "Durge Devi Namo Namah Durge Devi Namo Namah<br/>Mahishasura Mardini Jaya Jaya", "audio_url": "/audio/durge_devi_namo_namah.mp3"},
    {"title": "Ramachandra Prabhu", "deity": "Rama", "raga": "Mishra Kafi", "beat": "Keherwa", "lyrics": "Ramachandra Prabhu Ramachandra Prabhu<br/>Raghuvira Ranadhira Janaki Ram", "audio_url": "/audio/ramachandra_prabhu.mp3"},
    {"title": "Krishna Mukunda Murari", "deity": "Krishna", "raga": "Yaman", "beat": "Dadra", "lyrics": "Krishna Mukunda Murari Krishna Mukunda Murari<br/>Devaki Nandana Gopala", "audio_url": "/audio/krishna_mukunda_murari.mp3"},
    {"title": "Sai Ram Sai Shyam", "deity": "Sai", "raga": "Mishra Kafi", "beat": "Keherwa", "lyrics": "Sai Ram Sai Shyam Sai Ram Sai Shyam<br/>Shirdi Ke Sai Parthi Ke Sai", "audio_url": "/audio/sai_ram_sai_shyam.mp3"},
    {"title": "Maruti Raya Hanumanta", "deity": "Hanuman", "raga": "Bhupali", "beat": "Keherwa", "lyrics": "Maruti Raya Hanumanta Maruti Raya Hanumanta<br/>Anjani Putra Sankata Harana", "audio_url": "/audio/maruti_raya_hanumanta.mp3"},
    {"title": "Prathama Vandana Ganesha", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Adi", "lyrics": "Prathama Vandana Ganesha Prathama Vandana Ganesha<br/>Gajanana Vighna Vinashaka", "audio_url": "/audio/prathama_vandana_ganesha.mp3"},
    {"title": "Bholenath Mogra", "deity": "Shiva", "raga": "Darbari", "beat": "Keherwa", "lyrics": "Bholenath Mogra Bholenath Mogra<br/>Gangadhara Hara Bholenath", "audio_url": "/audio/bholenath_mogra.mp3"},
    {"title": "Amba Bhavani Sharade", "deity": "Devi", "raga": "Shankarabharanam", "beat": "Adi", "lyrics": "Amba Bhavani Sharade Amba Bhavani Sharade<br/>Jagadguru Pujita Sarada Maa", "audio_url": "/audio/amba_bhavani_sharade.mp3"},
    {"title": "Ayodhya Vasi Ram", "deity": "Rama", "raga": "Keeravani", "beat": "Keherwa", "lyrics": "Ayodhya Vasi Ram Ayodhya Vasi Ram<br/>Dasharatha Nandana Sai Ram", "audio_url": "/audio/ayodhya_vasi_ram.mp3"},
    {"title": "Radhe Shyam Gopal", "deity": "Krishna", "raga": "Yaman", "beat": "Dadra", "lyrics": "Radhe Shyam Gopal Radhe Shyam Gopal<br/>Govinda Murari Hari Bol", "audio_url": "/audio/radhe_shyam_gopal.mp3"},
    {"title": "Sadguru Deva Sai Ram", "deity": "Sai", "raga": "Bhupali", "beat": "Keherwa", "lyrics": "Sadguru Deva Sai Ram Sadguru Deva Sai Ram<br/>Parthi Purishvara Shirdi Vasi", "audio_url": "/audio/sadguru_deva_sai_ram.mp3"},
    {"title": "Veeranjaneya Jai", "deity": "Hanuman", "raga": "Mohanam", "beat": "Adi", "lyrics": "Veeranjaneya Jai Veeranjaneya Jai<br/>Maruti Raya Pavana Suta", "audio_url": "/audio/veeranjaneya_jai.mp3"},
    {"title": "Ganesha Sharanam Sharanam", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Keherwa", "lyrics": "Ganesha Sharanam Sharanam Ganesha Sharanam Sharanam<br/>Lambodara Jaya Vighneshvara", "audio_url": "/audio/ganesha_sharanam_sharanam.mp3"},
    {"title": "Hara Hara Shankara", "deity": "Shiva", "raga": "Shivaranjani", "beat": "Keherwa", "lyrics": "Hara Hara Shankara Hara Hara Shankara<br/>Samba Sadashiva Bholenath", "audio_url": "/audio/hara_hara_shankara.mp3"},
    {"title": "Sarva Mangala Mangalye", "deity": "Devi", "raga": "Durga", "beat": "Keherwa", "lyrics": "Sarva Mangala Mangalye Sarva Mangala Mangalye<br/>Shive Sarvartha Sadhike Sharanye", "audio_url": "/audio/sarva_mangala.mp3"},
    {"title": "Rama Kodanda Rama", "deity": "Rama", "raga": "Bhairavi", "beat": "Adi", "lyrics": "Rama Kodanda Rama Rama Kodanda Rama<br/>Janaki Vallabha Shrita Chintamani", "audio_url": "/audio/rama_kodanda_rama.mp3"},
    {"title": "Gopala Radha Lola", "deity": "Krishna", "raga": "Mishra Pilu", "beat": "Keherwa", "lyrics": "Gopala Radha Lola Gopala Radha Lola<br/>Radhe Shyam Govinda Jai", "audio_url": "/audio/gopala_radha_lola.mp3"},
    {"title": "Sai Baba Pravah", "deity": "Sai", "raga": "Yaman", "beat": "Keherwa", "lyrics": "Sai Baba Pravah Sai Baba Pravah<br/>Sabka Malik Ek Allah Sai", "audio_url": "/audio/sai_baba_pravah.mp3"},
    {"title": "Maruti Stotra Snippet", "deity": "Hanuman", "raga": "Bhupali", "beat": "Keherwa", "lyrics": "Maruti Stotra Snippet Maruti Stotra Snippet<br/>Rama Dootha Anjani Suta", "audio_url": "/audio/maruti_stotra_snippet.mp3"},
    {"title": "Gajanana He Gajanana", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Dadra", "lyrics": "Gajanana He Gajanana Gajanana He Gajanana<br/>Vighna Vinayaka Sai Gajanana", "audio_url": "/audio/gajanana_he_gajanana.mp3"},
    {"title": "Shiva Om Namah Shivaya", "deity": "Shiva", "raga": "Darbari", "beat": "Keherwa", "lyrics": "Shiva Om Namah Shivaya Shiva Om Namah Shivaya<br/>Om Namah Shivaya Chandrashekhara", "audio_url": "/audio/shiva_om_namah_shivaya.mp3"},
    {"title": "Sri Lakshmi Ramana", "deity": "Devi", "raga": "Kalyani", "beat": "Adi", "lyrics": "Sri Lakshmi Ramana Sri Lakshmi Ramana<br/>Narayani Namostute Maha Lakshmi", "audio_url": "/audio/sri_lakshmi_ramana.mp3"},
    {"title": "Ramakrishna Govinda", "deity": "Krishna", "raga": "Yaman", "beat": "Keherwa", "lyrics": "Ramakrishna Govinda Ramakrishna Govinda<br/>Bhaja Govinda Gopala Hari", "audio_url": "/audio/ramakrishna_govinda.mp3"},
    {"title": "Sai Prem Data", "deity": "Sai", "raga": "Mishra Kafi", "beat": "Keherwa", "lyrics": "Sai Prem Data Sai Prem Data<br/>Prema Swaroopa Sai Ram", "audio_url": "/audio/sai_prem_data.mp3"},
    {"title": "Pavanaputra Hanuman", "deity": "Hanuman", "raga": "Jog", "beat": "Keherwa", "lyrics": "Pavanaputra Hanuman Pavanaputra Hanuman<br/>Sankat Mochan Maruti Raya", "audio_url": "/audio/pavanaputra_hanuman.mp3"},
    {"title": "Gam Ganapataye Namaha", "deity": "Ganesha", "raga": "Hamsadhwani", "beat": "Keherwa", "lyrics": "Gam Ganapataye Namaha Gam Ganapataye Namaha<br/>Ganesha Mantra Siddhi Dayaka", "audio_url": "/audio/gam_ganapataye_namaha.mp3"},
    {"title": "Kailasavasi Shiva", "deity": "Shiva", "raga": "Bhairavi", "beat": "Keherwa", "lyrics": "Kailasavasi Shiva Kailasavasi Shiva<br/>Kailasa Parvata Vasi Shankara", "audio_url": "/audio/kailasavasi_shiva.mp3"},
    {"title": "Shradha Saburi Sai", "deity": "Sai", "raga": "Bhupali", "beat": "Keherwa", "lyrics": "Shradha Saburi Sai Shradha Saburi Sai<br/>Sai Baba Bhakti Mukti Prada", "audio_url": "/audio/shradha_saburi_sai.mp3"}
]

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Bhajan Source Mock</title>
</head>
<body>
    <div id="bhajans-container">
{cards}
    </div>
</body>
</html>
"""

card_template = """        <div class="bhajan-card">
            <h2 class="bhajan-title">{title}</h2>
            <span class="deity-name">{deity}</span>
            <span class="raga-name">{raga}</span>
            <span class="beat-name">{beat}</span>
            <div class="bhajan-lyrics">{lyrics}</div>
            <audio class="audio-player" src="{audio_url}"></audio>
        </div>"""

cards = []
for bh in bhajans:
    cards.append(card_template.format(**bh))

os.makedirs("backend/mock_data", exist_ok=True)
with open("backend/mock_data/bhajans_source.html", "w", encoding="utf-8") as f:
    f.write(html_template.format(cards="\n".join(cards)))

print("Successfully generated mock source file with 50 bhajans.")

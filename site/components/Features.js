import styles from '../styles/Features.module.css';
import Image from 'next/image';

function Features() {
    const featureList = [
      
        {
            title: 'Developer friendly declarative language to define dataPods',
            description: 'Building a data Product is as easy as commiting a YAML file to your code repository, just define what data your application needs and dataPi will take care of the rest.',
            image: '/images/declare.png',
        },
        {
            title: 'Deploy data products with dataPod containers',
            description: 'Keep your informational application logic close to your application with dataPods. Each dataPod exposes an contract based API and contains all the code and dependencies to run analytics independently without relying on your central LakeHouse infraestructure.',
            image: '/images/architecture.png',
        },
        // Add more features as needed
    ];

    return (
        <section className={styles.features}>
            <div className={styles.featureList}>
                {featureList.map((feature, index) => (
                    <div key={index} className={styles.feature}>
                        <div className={styles.imageWrapper}>
                            <Image 
                                src={feature.image} 
                                alt={feature.title} 
                                width={800}
                                height={600}
                                className={styles.roundedImage}
                                // layout="responsive" // Comment this out temporarily
                            />
                        </div>
                        <h3>{feature.title}</h3>
                        <p>{feature.description}</p>
                    </div>
                ))}
            </div>
        </section>
    );
}

export default Features;
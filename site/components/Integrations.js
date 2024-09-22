import styles from '../styles/Integrations.module.css';
import Image from 'next/image';

function Integrations() {
    const integrations = [
        { name: 'Ecosystem', image: '/images/integrations.png' },
      
        
    ];

    return (
        <section className={styles.integrations}>
            <h2>Integrations</h2>
            <div className={styles.integrationList}>
                {integrations.map((integration, index) => (
                    <div key={index} className={styles.integration}>
                        <Image src={integration.image} alt={integration.name} width={800} height={600} />
                    </div>
                ))}
            </div>
            <a href="https://github.com/velascoluis/datapi-core" className={styles.learnMore}>
                Learn More
            </a>
        </section>
    );
}

export default Integrations;
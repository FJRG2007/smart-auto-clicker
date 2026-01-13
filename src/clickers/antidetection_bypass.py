"""
Anti-Detection Bypass System for Smart Auto Clicker

Este modulo implementa tecnicas avanzadas de humanizacion para evadir
sistemas anti-cheat que detectan patrones de autoclickers.

Tecnicas implementadas:
1. Distribucion gaussiana (los humanos no tienen variacion uniforme)
2. Fatiga simulada (los humanos se cansan y ralentizan)
3. Micro-pausas aleatorias (distracciones humanas)
4. Burst clicking (rafagas de clicks como un humano)
5. Jitter natural del raton (temblor humano)
6. Variacion adaptativa (cambia patrones con el tiempo)
"""

import random
import math
import time
from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum

class BypassProfile(Enum):
    """Perfiles de bypass predefinidos."""
    LIGHT = "light"           # Variacion minima, para juegos con deteccion basica
    MODERATE = "moderate"     # Balance entre velocidad y seguridad
    AGGRESSIVE = "aggressive" # Maxima humanizacion, mas lento pero mas seguro
    ADAPTIVE = "adaptive"     # Se adapta automaticamente

@dataclass
class HumanizationConfig:
    """Configuracion del sistema de humanizacion."""
    # Distribucion gaussiana
    gaussian_sigma: float = 0.15  # Desviacion estandar (15% del intervalo base)

    # Sistema de fatiga
    fatigue_enabled: bool = True
    fatigue_rate: float = 0.001     # Incremento de delay por click
    fatigue_max: float = 0.3        # Maximo 30% mas lento
    fatigue_recovery: float = 0.05  # Recuperacion durante pausas

    # Micro-pausas
    micropause_chance: float = 0.02      # 2% de probabilidad por click
    micropause_min: float = 0.5          # Minimo 0.5 segundos
    micropause_max: float = 2.0          # Maximo 2 segundos

    # Long pauses (simulan distracciones)
    longpause_chance: float = 0.005      # 0.5% probabilidad
    longpause_min: float = 3.0           # Minimo 3 segundos
    longpause_max: float = 8.0           # Maximo 8 segundos

    # Burst clicking
    burst_enabled: bool = True
    burst_chance: float = 0.1            # 10% de entrar en modo burst
    burst_min_clicks: int = 3            # Minimo clicks en rafaga
    burst_max_clicks: int = 8            # Maximo clicks en rafaga
    burst_speed_multiplier: float = 0.6  # 60% del intervalo normal
    burst_cooldown: float = 1.5          # Pausa despues de rafaga

    # Jitter del raton
    mouse_jitter_enabled: bool = True
    mouse_jitter_pixels: int = 3         # Maximo pixeles de desviacion
    mouse_jitter_chance: float = 0.3     # 30% de clicks con jitter

    # Variacion de velocidad del raton
    mouse_speed_variation: float = 0.4   # +-40% variacion en velocidad

    # Ritmo variable
    rhythm_change_chance: float = 0.05   # 5% de cambiar ritmo base
    rhythm_variation: float = 0.2        # +-20% del ritmo base


class AntiDetectionBypass:
    """Sistema principal de bypass anti-deteccion."""

    PROFILES = {
        BypassProfile.LIGHT: HumanizationConfig(
            gaussian_sigma=0.08,
            fatigue_enabled=False,
            micropause_chance=0.01,
            longpause_chance=0.002,
            burst_enabled=False,
            mouse_jitter_enabled=False,
            rhythm_change_chance=0.02
        ),
        BypassProfile.MODERATE: HumanizationConfig(
            gaussian_sigma=0.12,
            fatigue_enabled=True,
            fatigue_rate=0.0005,
            fatigue_max=0.2,
            micropause_chance=0.015,
            longpause_chance=0.003,
            burst_enabled=True,
            burst_chance=0.08,
            mouse_jitter_enabled=True,
            mouse_jitter_pixels=2
        ),
        BypassProfile.AGGRESSIVE: HumanizationConfig(
            gaussian_sigma=0.2,
            fatigue_enabled=True,
            fatigue_rate=0.002,
            fatigue_max=0.4,
            micropause_chance=0.03,
            micropause_max=3.0,
            longpause_chance=0.008,
            longpause_max=12.0,
            burst_enabled=True,
            burst_chance=0.15,
            burst_max_clicks=12,
            mouse_jitter_enabled=True,
            mouse_jitter_pixels=5,
            mouse_jitter_chance=0.5,
            rhythm_change_chance=0.08
        ),
        BypassProfile.ADAPTIVE: HumanizationConfig()  # Default, se ajusta dinamicamente
    }

    def __init__(self, profile: BypassProfile = BypassProfile.MODERATE):
        self.profile = profile
        self.config = self.PROFILES.get(profile, HumanizationConfig())

        # Estado interno
        self.click_count = 0
        self.fatigue_level = 0.0
        self.current_rhythm_modifier = 1.0
        self.in_burst_mode = False
        self.burst_clicks_remaining = 0
        self.last_pause_time = time.time()
        self.session_start_time = time.time()

        # Estadisticas para modo adaptativo
        self.timing_history = []
        self.detection_score = 0.0

    def reset_session(self):
        """Reinicia el estado de la sesion."""
        self.click_count = 0
        self.fatigue_level = 0.0
        self.current_rhythm_modifier = 1.0
        self.in_burst_mode = False
        self.burst_clicks_remaining = 0
        self.last_pause_time = time.time()
        self.session_start_time = time.time()
        self.timing_history = []
        self.detection_score = 0.0

    def gaussian_variation(self, base: float) -> float:
        """
        Genera variacion usando distribucion gaussiana.
        Los humanos no tienen variacion uniforme - sus tiempos
        se agrupan alrededor de un valor central con cola.
        """
        sigma = base * self.config.gaussian_sigma
        variation = random.gauss(0, sigma)
        # Limitar variacion extrema (3 sigma)
        variation = max(-3 * sigma, min(3 * sigma, variation))
        return max(0.01, base + variation)

    def calculate_fatigue(self) -> float:
        """
        Calcula el factor de fatiga actual.
        Los humanos se cansan y sus clicks se vuelven mas lentos.
        """
        if not self.config.fatigue_enabled:
            return 0.0

        # Incrementar fatiga con cada click
        self.fatigue_level += self.config.fatigue_rate

        # Limitar fatiga maxima
        self.fatigue_level = min(self.fatigue_level, self.config.fatigue_max)

        # Recuperacion gradual durante pausas largas
        time_since_pause = time.time() - self.last_pause_time
        if time_since_pause > 5:  # Si paso mas de 5 segundos
            recovery = self.config.fatigue_recovery * (time_since_pause / 60)
            self.fatigue_level = max(0, self.fatigue_level - recovery)

        return self.fatigue_level

    def should_micropause(self) -> Tuple[bool, float]:
        """
        Determina si deberia ocurrir una micro-pausa.
        Simula distracciones humanas momentaneas.
        """
        if random.random() < self.config.micropause_chance:
            duration = random.uniform(
                self.config.micropause_min,
                self.config.micropause_max
            )
            return True, duration
        return False, 0.0

    def should_longpause(self) -> Tuple[bool, float]:
        """
        Determina si deberia ocurrir una pausa larga.
        Simula distracciones mayores (mirar telefono, etc).
        """
        if random.random() < self.config.longpause_chance:
            duration = random.uniform(
                self.config.longpause_min,
                self.config.longpause_max
            )
            self.last_pause_time = time.time()
            # Recuperar algo de fatiga durante pausa larga
            self.fatigue_level *= 0.7
            return True, duration
        return False, 0.0

    def check_burst_mode(self) -> bool:
        """
        Gestiona el modo burst (rafaga de clicks rapidos).
        Los humanos a veces hacen clicks rapidos en rafaga.
        """
        if not self.config.burst_enabled:
            return False

        # Si ya estamos en burst mode
        if self.in_burst_mode:
            self.burst_clicks_remaining -= 1
            if self.burst_clicks_remaining <= 0:
                self.in_burst_mode = False
                return False  # Siguiente sera el cooldown
            return True

        # Chance de entrar en burst mode
        if random.random() < self.config.burst_chance:
            self.in_burst_mode = True
            self.burst_clicks_remaining = random.randint(
                self.config.burst_min_clicks,
                self.config.burst_max_clicks
            )
            return True

        return False

    def update_rhythm(self):
        """
        Actualiza el modificador de ritmo.
        Los humanos cambian su velocidad de click con el tiempo.
        """
        if random.random() < self.config.rhythm_change_chance:
            change = random.uniform(
                -self.config.rhythm_variation,
                self.config.rhythm_variation
            )
            self.current_rhythm_modifier = max(0.7, min(1.3, 1.0 + change))

    def get_humanized_delay(self, base_interval: float) -> float:
        """
        Calcula el delay humanizado considerando todos los factores.

        Args:
            base_interval: Intervalo base en segundos

        Returns:
            Delay humanizado en segundos
        """
        self.click_count += 1

        # 1. Verificar pausas largas primero
        do_longpause, longpause_duration = self.should_longpause()
        if do_longpause:
            return longpause_duration

        # 2. Verificar micro-pausas
        do_micropause, micropause_duration = self.should_micropause()
        if do_micropause:
            return base_interval + micropause_duration

        # 3. Actualizar ritmo periodicamente
        self.update_rhythm()

        # 4. Verificar burst mode
        in_burst = self.check_burst_mode()

        # 5. Calcular intervalo base con modificadores
        interval = base_interval * self.current_rhythm_modifier

        if in_burst:
            interval *= self.config.burst_speed_multiplier

        # 6. Aplicar fatiga
        fatigue = self.calculate_fatigue()
        interval *= (1 + fatigue)

        # 7. Aplicar variacion gaussiana
        interval = self.gaussian_variation(interval)

        # 8. Cooldown post-burst
        if not self.in_burst_mode and self.burst_clicks_remaining == 0 and in_burst:
            interval += random.uniform(
                self.config.burst_cooldown * 0.8,
                self.config.burst_cooldown * 1.2
            )

        # Guardar para estadisticas
        self.timing_history.append(interval)
        if len(self.timing_history) > 100:
            self.timing_history.pop(0)

        return max(0.01, interval)

    def get_mouse_jitter(self, target_x: int, target_y: int) -> Tuple[int, int]:
        """
        Aplica jitter natural al objetivo del raton.
        Simula el temblor humano natural.

        Args:
            target_x: Coordenada X objetivo
            target_y: Coordenada Y objetivo

        Returns:
            Coordenadas con jitter aplicado
        """
        if not self.config.mouse_jitter_enabled:
            return target_x, target_y

        if random.random() > self.config.mouse_jitter_chance:
            return target_x, target_y

        # Jitter gaussiano (mas realista que uniforme)
        jitter_x = int(random.gauss(0, self.config.mouse_jitter_pixels / 2))
        jitter_y = int(random.gauss(0, self.config.mouse_jitter_pixels / 2))

        return target_x + jitter_x, target_y + jitter_y

    def get_mouse_movement_params(self) -> dict:
        """
        Genera parametros humanizados para movimiento del raton.

        Returns:
            Dict con steps, delay_base, y curva de movimiento
        """
        # Numero variable de pasos
        steps = random.randint(8, 25)

        # Velocidad variable
        base_delay = 0.005
        speed_mod = 1 + random.uniform(
            -self.config.mouse_speed_variation,
            self.config.mouse_speed_variation
        )
        delay = base_delay * speed_mod

        # Tipo de curva (lineal, ease-in, ease-out, ease-in-out)
        curve_types = ['linear', 'ease_in', 'ease_out', 'ease_in_out']
        curve_weights = [0.2, 0.25, 0.25, 0.3]
        curve = random.choices(curve_types, weights=curve_weights)[0]

        return {
            'steps': steps,
            'delay': delay,
            'curve': curve
        }

    def apply_movement_curve(self, t: float, curve_type: str) -> float:
        """
        Aplica una curva de movimiento al progreso.

        Args:
            t: Progreso normalizado (0-1)
            curve_type: Tipo de curva

        Returns:
            Progreso modificado por la curva
        """
        if curve_type == 'linear':
            return t
        elif curve_type == 'ease_in':
            return t * t
        elif curve_type == 'ease_out':
            return 1 - (1 - t) ** 2
        elif curve_type == 'ease_in_out':
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - ((-2 * t + 2) ** 2) / 2
        return t

    def get_hold_duration(self, base_duration: float) -> float:
        """
        Genera duracion humanizada para hold.

        Args:
            base_duration: Duracion base en segundos

        Returns:
            Duracion humanizada
        """
        # Variacion gaussiana
        duration = self.gaussian_variation(base_duration)

        # Aplicar fatiga (holds mas largos cuando cansado)
        fatigue = self.calculate_fatigue()
        duration *= (1 + fatigue * 0.5)

        return max(0.01, duration)

    def get_detection_risk_score(self) -> float:
        """
        Calcula un score de riesgo de deteccion basado en patrones.
        Util para el modo adaptativo.

        Returns:
            Score de 0 (seguro) a 1 (alto riesgo)
        """
        if len(self.timing_history) < 10:
            return 0.0

        # Calcular desviacion estandar
        mean = sum(self.timing_history) / len(self.timing_history)
        variance = sum((x - mean) ** 2 for x in self.timing_history) / len(self.timing_history)
        std_dev = math.sqrt(variance)

        # Coeficiente de variacion (CV)
        cv = std_dev / mean if mean > 0 else 0

        # Un CV muy bajo indica patrones muy regulares (sospechoso)
        # Un CV muy alto indica patrones muy erraticos (tambien sospechoso)

        # CV ideal para humanos: 0.15-0.35
        if cv < 0.1:
            risk = (0.1 - cv) * 5  # Demasiado regular
        elif cv > 0.5:
            risk = (cv - 0.5) * 2  # Demasiado erratico
        else:
            risk = 0.0

        return min(1.0, max(0.0, risk))

    def adapt_profile(self):
        """
        Adapta la configuracion basandose en el riesgo de deteccion.
        Solo para perfil ADAPTIVE.
        """
        if self.profile != BypassProfile.ADAPTIVE:
            return

        risk = self.get_detection_risk_score()

        if risk > 0.7:
            # Alto riesgo: aumentar humanizacion
            self.config.gaussian_sigma = min(0.25, self.config.gaussian_sigma + 0.02)
            self.config.micropause_chance = min(0.05, self.config.micropause_chance + 0.005)
        elif risk < 0.2:
            # Bajo riesgo: podemos ser un poco mas agresivos
            self.config.gaussian_sigma = max(0.1, self.config.gaussian_sigma - 0.01)
            self.config.micropause_chance = max(0.01, self.config.micropause_chance - 0.002)

    def get_stats(self) -> dict:
        """
        Obtiene estadisticas de la sesion actual.

        Returns:
            Dict con estadisticas
        """
        session_duration = time.time() - self.session_start_time
        avg_interval = sum(self.timing_history) / len(self.timing_history) if self.timing_history else 0

        return {
            'click_count': self.click_count,
            'session_duration': session_duration,
            'fatigue_level': self.fatigue_level,
            'current_rhythm': self.current_rhythm_modifier,
            'average_interval': avg_interval,
            'detection_risk': self.get_detection_risk_score(),
            'profile': self.profile.value
        }

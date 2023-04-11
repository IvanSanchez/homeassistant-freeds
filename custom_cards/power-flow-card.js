/**
 * PowerFlowCard component for the Home Assistant UI.
 *
 * © 2023 Iván Sánchez Ortega <ivan@sanchezortega.es>. Licensed under GPLv3.
 */


/*

To display this card, edit a dashboard and add a card with a custom YAML
configuration. The YAML for this card should look like:

type: custom:power-flow-card
sources:
 - entity: sensor.solar_power_watts
   inverse: false
 - entity: sensor.wind_power_watts
   inverse: false
sinks:
 - entity: sensor.boiler_watts
   inverse: false
left_exchanger:
  entity: sensor.grid_watts
  inverse: false
right_exchanger:
  entity: sensor.battery_watts
  inverse: false


Sources should have a positive value when PRODUCING power.

Sinks should have a positive value when CONSUMING power.

Exchangers should have a positive value when PRODUCING power.

If any of the entities in your system behaves differently, set `inverse` to `true`.

*/


class PowerFlowCard extends HTMLElement {
	// The raw configuration passed by HASS
	#config;

	// A map of entity names to PowerFlowNode elements
	#nodes = {};

	// The default power sink
	#defaultSink;

	// An array of entity names with positive value for default sink calculations
	#positives = [];

	// An array of entity names with negative value for default sink calculations
	#negatives = [];

	constructor() {
		super()
	}

	// Whenever the state changes, a new `hass` object is set. Use this to
	// update your content.
	set hass(hass) {

		for (const [entity, node] of Object.entries(this.#nodes)) {
			node.state = hass.states[entity];
		}

		// Calculate value of power sink
		if (!this.#defaultSink) {return}
		let sunk = 0;
		for (const positive of this.#positives) {
			const v = Number(hass.states[positive].state);
			if (isNaN(v)) {
				sunk = NaN;
			} else {
				sunk += v;
			}
		}
		for (const negative of this.#negatives) {
			const v = Number(hass.states[negative].state);
			if (isNaN(v)) {
				sunk = NaN;
			} else {
				sunk -= v;
			}
		}

		if (isNaN(sunk)) {
			this.#defaultSink.state = {
				attributes:{icon: 'mdi:home'},
				state: NaN,
				entity_id: ""
			}
		} else {
			this.#defaultSink.state = {
				attributes:{icon: 'mdi:home'},
				state: sunk.toFixed(1),
				entity_id: ""
			}
		}

		let maxAbsolute = sunk;
		for (const [entity, node] of Object.entries(this.#nodes)) {
			node.state = hass.states[entity];
			maxAbsolute = Math.max(maxAbsolute, Math.abs(node.state?.state));
		}
		if (!isNaN(maxAbsolute)) {
			for (const [entity, node] of Object.entries(this.#nodes)) {
				node.setArrowWidth(10 * Math.abs(node.state.state) / maxAbsolute);
			}
			this.#defaultSink.setArrowWidth(10 * sunk / maxAbsolute);
		}

	}

	// The user supplied configuration. Throw an exception and Home Assistant
	// will render an error card.
	setConfig(config) {
		if (! (config.sources instanceof Array)) {
			throw new Error("You need to define at least one power source");
		}
		this.#config = config;
	}

	connectedCallback(){
		// console.log('power flow connected to document. config: ', this.#config);
		this.#nodes = [];
		this.#positives = [];
		this.#negatives = [];

		const itemsWide = Math.max(this.#config.sources.length,
								   (this.#config.sinks?.length ?? 0) + 1);

		const pxWide = 84 * itemsWide + 220;

		this.innerHTML = `
			<ha-card header="Power Flow">
			<div style='margin: 0 auto 10px auto; width: ${pxWide}px'>
				<div id="power-sources" style='text-align: center'></div>
				<div id="power-center" style='height:80px; width: ${pxWide}px; position:relative;'>
					<div id="power-left-exchanger" style='position:absolute; left:0;'></div>
					<div id="power-hub" style='
						background: var(--lovelace-background, #fafafa);
						position:absolute;
						left:111px; right: 111px; height: 80px;
						border-color: var(--ha-card-border-color, #e0e0e0);
						border-radius: var(--ha-card-border-radius, 12px);
						border-width: var(--ha-card-border-width, 1px);
						border-style: solid;
						'></div>
					<div id="power-right-exchanger" style='position:absolute; right:0;'></div>
				</div>
				<div id="power-sinks" style='text-align: center'></div>
			</div>
			</ha-card>
		`;

		const srcCnt = this.querySelector("#power-sources");
		const snkCnt = this.querySelector("#power-sinks");
		const leftCnt = this.querySelector("#power-left-exchanger");
		const rightCnt = this.querySelector("#power-right-exchanger");

		this.#config.sources.forEach(({entity, inverted})=>{
			const node = new PowerFlowNode(SOURCE, inverted);

			srcCnt.appendChild(node);

			this.#nodes[entity] = node;
			if (inverted) {
				this.#negatives.push(entity)
			} else {
				this.#positives.push(entity)
			}
		})

		if (this.#config.sinks) {
			this.#config.sinks.forEach(({entity, inverted})=>{
				const node = new PowerFlowNode(SINK, inverted);

				snkCnt.appendChild(node);

				this.#nodes[entity] = node;

				if (inverted) {
					this.#positives.push(entity)
				} else {
					this.#negatives.push(entity)
				}
			})
		}

		snkCnt.appendChild(this.#defaultSink = new PowerFlowNode(SINK));

		if (this.#config.left_exchanger) {
			const {entity, inverted} = this.#config.left_exchanger;
			const node = new PowerFlowNode(LEFT_EXCHANGE, inverted);
			leftCnt.appendChild(node)
			this.#nodes[entity] = node;
			if (inverted) {
				this.#negatives.push(entity)
			} else {
				this.#positives.push(entity)
			}
		}

		if (this.#config.right_exchanger) {
			const {entity, inverted} = this.#config.right_exchanger;
			const node = new PowerFlowNode(RIGHT_EXCHANGE, inverted);
			rightCnt.appendChild(node)
			this.#nodes[entity] = node;
			if (inverted) {
				this.#negatives.push(entity)
			} else {
				this.#positives.push(entity)
			}
		}

	}

	// The height of your card. Home Assistant uses this to automatically
	// distribute all cards over the available columns.
	getCardSize() {
		return 3;
	}
}

const SOURCE = Symbol("Source");
const SINK = Symbol("Sink");
const LEFT_EXCHANGE = Symbol("Left exchange");
const RIGHT_EXCHANGE = Symbol("Right exchange");

class PowerFlowNode extends HTMLElement {
	#icon;
	#state;
	#text;
	#arrow;
	#arrowpath;
	#role;
	#inverted;

	constructor(role, inverted) {
		super();
		this.#role = role;
		this.#inverted = !!inverted;


		// Mimicking the style of the elements in the default daily energy graphic
		this.style.height = '80px';
		this.style.width = '80px';
		this.style.borderRadius = "50%";
		this.style.border = "2px solid";
		this.style.display = 'inline-block';
		this.style.textAlign = 'center';
		this.style.position = 'relative';

		switch (this.#role) {
			case SOURCE:
				this.style["border-color"] = "var(--energy-solar-color)";
				break;
			case SINK:
				this.style["border-color"] = "var(--energy-gas-color)";
				break;
			case LEFT_EXCHANGE:
				this.style["border-color"] = "var(--energy-grid-return-color)";
				break;
			case RIGHT_EXCHANGE:
				this.style["border-color"] = "var(--energy-battery-in-color)";
				break;
		}
		// --energy-grid-consumption-color: #488fc2;
		// --energy-grid-return-color: #8353d1;
		// --energy-solar-color: #ff9800;
		// --energy-non-fossil-color: #0f9d58;
		// --energy-battery-out-color: #4db6ac;
		// --energy-battery-in-color: #f06292;
		// --energy-gas-color: #8E021B;
		// --energy-water-color: #00bcd4;
	}

	connectedCallback(){
		// this.appendChild(this.#icon = document.createElement('ha-state-icon'));


		this.#arrow = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
		this.#arrow.style.position = 'absolute';
		this.#arrow.style.width = '80px';
		this.#arrow.style.height = '30px';

		this.#arrow.innerHTML = `<defs><marker id='head' orient="auto" markerWidth='3' markerHeight='4' refX='0.1' refY='2'><path d='M0,0 V4 L2,2 Z' fill="black"/></marker></defs>
		<path id='arrow-line' marker-end='url(#head)' stroke-width='2' fill='none' stroke='black' d='M40,0 L40,20' />`

		if (this.#role == SOURCE) {
			this.appendChild(this.#icon = document.createElement('state-badge'));
			this.appendChild(this.#text = document.createElement('div'));
			this.#icon.style.marginTop = '4px';
			this.style.marginBottom = '30px';
			this.#arrow.style.bottom = '-32px';
			this.#arrow.style.left = '0';
		} else if (this.#role == SINK) {
			this.appendChild(this.#text = document.createElement('div'));
			this.appendChild(this.#icon = document.createElement('state-badge'));
			this.#text.style.marginTop = '22px';
			this.style.marginTop = '30px';
			this.#arrow.style.top = '-32px';
			this.#arrow.style.left = '0';
		} else if (this.#role == LEFT_EXCHANGE) {
			this.appendChild(this.#icon = document.createElement('state-badge'));
			this.appendChild(this.#text = document.createElement('div'));
			this.#icon.style.marginTop = '16px';
			this.#text.style.position = 'absolute';
			this.#text.style.width = '80px';
			this.#text.style.left= '0';
			this.#arrow.style.transform= "rotate(90deg)";
			this.#arrow.style.right= "-54px";
			this.#arrow.style.top= "25px";
		} else if (this.#role == RIGHT_EXCHANGE) {
			this.appendChild(this.#icon = document.createElement('state-badge'));
			this.appendChild(this.#text = document.createElement('div'));
			this.#icon.style.marginTop = '16px';
			this.#text.style.position = 'absolute';
			this.#text.style.width = '80px';
			this.#text.style.right= '0';
			this.#arrow.style.left= "-54px";
			this.#arrow.style.transform= "rotate(90deg)";
			this.#arrow.style.top= "25px"
		} else {
			throw new Error("Bad role for PowerFlowNode");
		}

		this.appendChild(this.#arrow);
		this.#arrowpath = this.#arrow.querySelector("path#arrow-line");
	}

	get state() {
		return this.#state;
	}

	set state(s) {
		this.#state = s;

		this.#icon.stateObj = s;

		if (s.state && !isNaN(s.state)) {
			const v = (this.#inverted ? -s.state : s.state);
			this.#text.innerText = v + " W";
			if (this.#role === LEFT_EXCHANGE) {
				if (v > 0) {
					this.#text.style.top = '8px';
					this.#text.style.bottom = 'auto';
					this.#arrow.style.transform= "rotate(-90deg)";
					this.#arrow.style.top= "10px";
				} else {
					this.#text.style.top = 'auto';
					this.#text.style.bottom = '8px';
					this.#arrow.style.transform= "rotate(90deg)";
					this.#arrow.style.top="40px";
				}
			}
			else if (this.#role === RIGHT_EXCHANGE) {
				if (v > 0) {
					this.#text.style.top = '8px';
					this.#text.style.bottom = 'auto';
					this.#arrow.style.transform= "rotate(90deg)";
					this.#arrow.style.top= "10px";
				} else {
					this.#text.style.top = 'auto';
					this.#text.style.bottom = '8px';
					this.#arrow.style.transform= "rotate(-90deg)";
					this.#arrow.style.top="40px";
				}
			}
		} else {
			this.#text.innerText = 'N/A';
		}
	}

	setArrowWidth(w) {
		this.#arrowpath.attributes['stroke-width'].value = w;
		this.#arrowpath.attributes['d'].value = `M40,0 L40,${30-w*2}`
	}
}


customElements.define("power-flow-node", PowerFlowNode);
customElements.define("power-flow-card", PowerFlowCard);

